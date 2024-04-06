import os
import logging
import requests
import base64

from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, ContextTypes, CallbackContext

from ai_datahive.publishers.models import TelegramMessage, TelegramGroupTopic

from ai_datahive.utils.dao_factory import get_dao
from ai_datahive.dao import BaseDAO


def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! This is the TelegramGroupNotifier.')


def create_telegram_application() -> Application:
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    application = Application.builder().token(telegram_token).build()
    # application.add_handler(CommandHandler('start', start_command))
    return application


def get_new_messages(dao: BaseDAO) -> list[TelegramMessage]:
    now = datetime.utcnow()
    # Fetch messages where 'schedule_for' is null or less than the current time, and 'sent_at' is null.
    filters = [
        ["or", ["scheduled_for", "lte", now.isoformat()], ["scheduled_for", "is", "null"]],
        ["sent_at", "is", "null"]
    ]
    tmsgs = dao.read(TelegramMessage, filters=filters,
                     order_by="created_at")

    return tmsgs


async def process_and_send_new_messages(context: CallbackContext):
    chat_id = os.getenv("CHAT_ID")
    dao: BaseDAO = context.job.data['dao']

    new_messages = get_new_messages(dao)

    if new_messages:
        for message in new_messages:
            await send_message(dao, context, chat_id, message)
            update_message_status(dao, message)


async def send_message(dao: BaseDAO, context: CallbackContext, chat_id: str, message: TelegramMessage):
    def split_content(content, max_length):
        return [content[i:i + max_length] for i in range(0, len(content), max_length)]

    content = message.content

    parse_mode = 'HTML' if content and '<' in content and '>' in content else None
    media = await prepare_media(message)

    message_thread_id = get_message_thread_id_by_topic_name(dao, message.telegram_group_topic_fk)
    #message_thread_id = get_message_thread_id_by_topic_name(supabase_client, topic) # COmmeted because bad db design with string

    max_message_length = int(os.getenv("TELEGRAM_MAX_MESSAGE_LENGTH", 4096))
    max_caption_length = int(os.getenv("TELEGRAM_MAX_CAPTION_LENGTH", 1024))

    media_methods = {
        'image': context.bot.send_photo,
        'video': context.bot.send_video,
        'audio': context.bot.send_audio,
    }

    base_args = {'chat_id': chat_id, 'message_thread_id': message_thread_id, 'parse_mode': parse_mode}

    message_object = None
    if message.media_type in media_methods and media:
        if content:
            if len(content) > max_caption_length:
                caption = content[:max_caption_length]
                rest_content = content[max_caption_length:]
            else:
                caption = content
                rest_content = None
        else:
            caption = None
            rest_content = None

        # Ergänzen der spezifischen Argumente für Medientypen
        send_method = media_methods[message.media_type]
        media_args = {'caption': caption} if content else {}
        media_args.update(base_args)
        await send_method(photo=media if message.media_type == 'image' else media, **media_args)
        if rest_content:
            for part in split_content(rest_content, max_message_length):
                await context.bot.send_message(text=part, **base_args)
    elif content:
        # Senden einer Textnachricht, falls kein Medieninhalt vorhanden oder erforderlich ist
        for part in split_content(content, max_message_length):
            await context.bot.send_message(text=part, **base_args)
    else:
        # Für den Fall, dass weder Inhalt noch Medien vorhanden sind (kann erweitert werden, falls nötig)
        print("Kein Inhalt oder Medien zum Senden vorhanden.")



    # TODO make it cleaner
    #message_object = None

    #if message.media_type == 'image' and content and media:
    #    message_object = await context.bot.send_photo(chat_id=chat_id, photo=media, message_thread_id=message_thread_id,caption=content, parse_mode=parse_mode)
    #elif message.media_type == 'video' and content and media:
    #    message_object = await context.bot.send_video(chat_id=chat_id, video=media, message_thread_id=message_thread_id,caption=content, parse_mode=parse_mode)
    #elif message.media_type == 'audio' and content and media:
    #    message_object = await context.bot.send_audio(chat_id=chat_id, audio=media, message_thread_id=message_thread_id,caption=content, parse_mode=parse_mode)
    #elif content:
    #    message_object = await context.bot.send_message(chat_id=chat_id, message_thread_id=message_thread_id, text=content, parse_mode=parse_mode)
    #elif media:
    #    if message.media_type == 'image':
    #        message_object = await context.bot.send_photo(chat_id=chat_id, photo=media, message_thread_id=message_thread_id)
    #    elif message.media_type == 'video':
    #        message_object = await context.bot.send_video(chat_id=chat_id, video=media, message_thread_id=message_thread_id)
    #    elif message.media_type == 'audio':
    #        message_object = await context.bot.send_audio(chat_id=chat_id, audio=media, message_thread_id=message_thread_id)

    #TODO: Thinking about pinning the message
    #if message_object:
    #    await context.bot.pin_chat_message(chat_id=chat_id, message_id=message_object.message_id)


def get_message_thread_id_by_topic_name(dao: BaseDAO, telegram_group_topic_fk: str):
    tgt = dao.read(TelegramGroupTopic, filters=[["id", telegram_group_topic_fk]], limit=1)
    if tgt:
        return tgt[0].telegram_group_topic_id
    else:
        return None


async def prepare_media(message: TelegramMessage):
    media_content = message.media_content
    media_url = message.media_url

    if media_content:
        return BytesIO(base64.b64decode(media_content))
    elif media_url:
        response = requests.get(media_url)
        return BytesIO(response.content)
    return None


def update_message_status(dao: BaseDAO, message: TelegramMessage):
    now = datetime.utcnow()
    message.sent_at = now.isoformat()
    message.status = 'sent'
    dao.update(message)


def main():
    setup_logging()
    load_dotenv()

    dao: BaseDAO = get_dao()
    telegram_application: Application = create_telegram_application()

    (telegram_application.job_queue.run_repeating(process_and_send_new_messages,
                                                  interval=10, first=0, data={'dao': dao}))

    print('Telegram Bot started ...')
    # Run the bot until the user presses Ctrl-C
    telegram_application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
