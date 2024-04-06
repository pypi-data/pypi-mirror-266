from typing import Union, List

from ai_datahive.publishers import TelegramMessage, TelegramGroup, TelegramGroupTopic

from ai_datahive.transformers import Content


class TelegramBaseLoader:
    def __init__(self, telegram_group_name, telegram_group_topic_id):
        from ai_datahive.utils.dao_factory import dao_factory
        self.dao = dao_factory()

        tgr = self.dao.read(TelegramGroup, [["telegram_group_name", telegram_group_name]], limit=1)
        if not tgr:
            raise ValueError(f"Telegram-Gruppe '{telegram_group_name}' nicht gefunden.")

        self.telegram_group_uuid = tgr[0].id
        self.telegram_group_topic_id = telegram_group_topic_id

    def retrieve(self):
        raise NotImplementedError

    def find_group_topic_uuid(self):
        filters = [
            ["telegram_group_topic_id", self.telegram_group_topic_id],
            ["telegram_group_fk", self.telegram_group_uuid]
        ]

        group_topic = self.dao.read(TelegramGroupTopic, filters, limit=1)
        if group_topic:
            return group_topic[0].id
        else:
            return None

    def save_content_as_telegram_message(self, content: Union[Content, List[Content]]):
        group_topic_uuid = self.find_group_topic_uuid()
        if not group_topic_uuid:
            print("Keine entsprechende group_topic_id gefunden.")
            return

        if isinstance(content, list):
            str_content = '\n\n'.join([c.content for c in content])
            content = content[0]
        else:
            str_content = content.content

        # Datenstruktur für die neue Nachricht
        message_data = {
            'telegram_group_topic_fk': group_topic_uuid,
            'content': f"<b>{content.title}</b>\n\n{str_content}",
            'creator': content.creator,
            'status': 'planned'
        }

        if content.media_type and (content.media_url or content.media_content):
            message_data['media_type'] = content.media_type
            if content.media_url:
                message_data['media_url'] = content.media_url
            elif content.media_content:
                message_data['media_content'] = content.media_content

        # Füge `schedule_for` hinzu, wenn ein Zeitpunkt angegeben ist
        if content.scheduled_for:
            message_data['schedule_for'] = content.schedule_for

        # Speichern der Nachricht in der Tabelle `t_telegram_messages`
        result = self.dao.create(TelegramMessage(**message_data))

    def load(self):
        content = self.retrieve()
        self.save_content_as_telegram_message(content)
