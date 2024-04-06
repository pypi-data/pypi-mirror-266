from ai_datahive.transformers import Content

from ai_datahive.utils import today_as_start_and_enddate_str

from ai_datahive.publishers import TelegramBaseLoader


class TelegramTopDailyImageLoader(TelegramBaseLoader):

    def __init__(self, telegram_group_name, telegram_group_topic_id):
        super().__init__(telegram_group_name, telegram_group_topic_id)

    def retrieve(self):
        start_date_str, end_date_str = today_as_start_and_enddate_str()
        filters = [
            ["creator", "TopDailyImage"],
            ["language", "de"],
            ["created_at", "between", start_date_str, end_date_str]
        ]

        topimage = self.dao.read(Content, filters, limit=1)
        return topimage[0]


def main():
    from dotenv import load_dotenv
    load_dotenv()
    loader = TelegramTopDailyImageLoader('KI & Business', 27)
    loader.load()


if __name__ == '__main__':
    main()
