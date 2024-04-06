from ai_datahive.transformers.models import Content

from ai_datahive.publishers.loader import TelegramBaseLoader
from ai_datahive.utils.datetime_helper import today_as_start_and_enddate_str, get_start_and_end_times_based_on_interval


class TelegramDailyTrendingGithubProjectsLoader(TelegramBaseLoader):
    def __init__(self, telegram_group_name, telegram_group_topic_id,
                 creator='TelegramDailyTrendingGithubProjectsLoader', language='de'):
        super().__init__(creator, language, telegram_group_name, telegram_group_topic_id)

    def retrieve(self):
        if self.run_interval:
            start_date_str, end_date_str = get_start_and_end_times_based_on_interval(self.run_interval)
        else:
            start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [
            ["creator", "DailyTrendingGithubProjectTransformer"],
            ["lang", self.language],
            ["created_at", "between", start_date_str, end_date_str]
        ]

        projects = self.dao.read(Content, filters, limit=3)

        for project in projects:
            project.title = 'Aktuelle GitHub-Trends'

        return projects


def main():
    from dotenv import load_dotenv
    load_dotenv()
    PROJECTS_GROUP_TOPIC_ID = 20
    loader = TelegramDailyTrendingGithubProjectsLoader('KI & Business', PROJECTS_GROUP_TOPIC_ID)
    loader.load()


if __name__ == '__main__':
    main()
