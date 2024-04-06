from ai_datahive.transformers.models import Content

from ai_datahive.utils.datetime_helper import today_as_start_and_enddate_str, get_start_and_end_times_based_on_interval

from ai_datahive.publishers.loader import TelegramBaseLoader


class TelegramTopDailyImageCritiqueLoader(TelegramBaseLoader):

    def __init__(self, telegram_group_name, telegram_group_topic_id, creator='TelegramTopDailyImageCritiqueLoader',
                 language='de'):
        super().__init__(creator, language, telegram_group_name, telegram_group_topic_id)

    def retrieve(self):
        if self.run_interval:
            start_date_str, end_date_str = get_start_and_end_times_based_on_interval(self.run_interval)
        else:
            start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [
            ["creator", "DailyImageCritiqueJS"],
            ["lang", self.language],
            ["created_at", "between", start_date_str, end_date_str]
        ]

        topimage = self.dao.read(Content, filters, limit=1)
        if topimage:
            return topimage[0]
        return None


def main():
    from dotenv import load_dotenv
    load_dotenv()
    IMAGE_GROUP_TOPIC_ID = 27
    loader = TelegramTopDailyImageCritiqueLoader('KI & Business', IMAGE_GROUP_TOPIC_ID)
    loader.load()


if __name__ == '__main__':
    main()
