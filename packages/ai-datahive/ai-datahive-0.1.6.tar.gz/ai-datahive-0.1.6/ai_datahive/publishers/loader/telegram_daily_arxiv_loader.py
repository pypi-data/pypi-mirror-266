from ai_datahive.transformers.models import Content

from ai_datahive.publishers.loader import TelegramBaseLoader
from ai_datahive.utils.datetime_helper import get_start_and_end_times_based_on_interval, today_as_start_and_enddate_str


class TelegramDailyArxivLoader(TelegramBaseLoader):

    def __init__(self, telegram_group_name, telegram_group_topic_id, creator='TelegramDailyArxivLoader', language='de'):
        super().__init__(creator, language, telegram_group_name, telegram_group_topic_id)

    def retrieve(self):
        if self.run_interval:
            start_date_str, end_date_str = get_start_and_end_times_based_on_interval(self.run_interval)
        else:
            start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [
            ["creator", "DailyArxivPaperTransformer"],
            ["lang", self.language],
            ["created_at", "between", start_date_str, end_date_str]  # TODO extract from run_interval
        ]

        paper = self.dao.read(Content, filters, limit=1)
        if len(paper) > 0:
            return paper[0]
        return None


def main():
    from dotenv import load_dotenv
    load_dotenv()
    ARXIV_GROUP_TOPIC_ID = 2
    loader = TelegramDailyArxivLoader('KI & Business', ARXIV_GROUP_TOPIC_ID)
    loader.load()


if __name__ == '__main__':
    main()
