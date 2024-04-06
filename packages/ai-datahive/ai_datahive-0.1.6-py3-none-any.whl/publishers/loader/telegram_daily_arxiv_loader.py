from ai_datahive.transformers import Content

from ai_datahive.utils import today_as_start_and_enddate_str

from ai_datahive.publishers import TelegramBaseLoader


class TelegramDailyArxivLoader(TelegramBaseLoader):

    def __init__(self, telegram_group_name, telegram_group_topic_id):
        super().__init__(telegram_group_name, telegram_group_topic_id)

    def retrieve(self):
        start_date_str, end_date_str = today_as_start_and_enddate_str()
        filters = [
            ["creator", "DailyArxivPaper"],
            ["language", "de"],
            ["created_at", "between", start_date_str, end_date_str]
        ]

        paper = self.dao.read(Content, filters, limit=1)
        return paper[0]


def main():
    from dotenv import load_dotenv
    load_dotenv()
    ARXIV_GROUP_TOPIC_ID = 2
    loader = TelegramDailyArxivLoader('KI & Business', ARXIV_GROUP_TOPIC_ID)
    loader.load()


if __name__ == '__main__':
    main()
