import os

from dotenv import load_dotenv
from ai_datahive.collectors import BaseCollector

from ai_datahive.collectors.utils.allowed_github_parameter import AllowedDateRanges
from ai_datahive.collectors.utils.scraping_helper import get_request
from ai_datahive.collectors.utils.github_helper import filter_articles, make_soup, scraping_repositories

from ai_datahive.collectors.models import GithubProject

from ai_datahive.utils import datetime_helper as dh


class GithubCollector(BaseCollector):

    VALID_PERIODS = ['Day', 'Week', 'Month']

    #TODO if needed use more parameters, right now fixed to github trending repos
    def __init__(self, creator='GithubCollector', period='Day', tags=None, limit=3):
        self.creator = creator
        self.limit = limit
        self.period = period
        self.media_type = 'github_project'
        self.github_url = os.getenv('GITHUB_TRENDS_URL')

        if tags is None:
            self.tags = self.build_tags(period)
        else:
            self.tags = tags

        self.validate_parameters(period)

        super().__init__(creator=self.creator, content_type=GithubProject)

    def validate_parameters(self, period):
        if period not in self.VALID_PERIODS:
            raise ValueError(f"period must be one of {self.VALID_PERIODS}")

    def build_tags(self, period):
        tags = 'github, '
        tags += 'trending, '
        tags += dh.to_periodic_format(period) + ', '

        tags = tags.rstrip(', ')
        return tags

    def trending_repositories(self, since: AllowedDateRanges = None):
        """Returns data about trending repositories (all programming
        languages, cannot be specified on this endpoint)."""
        if since:
            payload = {"since": since}
        else:
            payload = {"since": "weekly"}

        raw_html = get_request(self.github_url, payload)
        articles_html = filter_articles(raw_html)
        soup = make_soup(articles_html)
        return scraping_repositories(soup, since=payload[
            "since"])

    def retrieve(self):
        periodicity = dh.to_periodic_format(self.period)
        entries = self.trending_repositories(since=periodicity)
        projects = self.convert_to_github_project_entities(entries)
        return projects[:self.limit]

    def convert_to_github_project_entities(self, data):
        result = []
        if data:
            for item in data:

                contributors = [user['username'] for user in item['builtBy']]

                # Format output
                if len(contributors) > 3:
                    output = ', '.join(contributors[:3]) + ', et al.'
                else:
                    output = ', '.join(contributors)

                project = GithubProject(
                    creator=self.creator,
                    rank=item['rank'],
                    username=item['username'],
                    name=item['repositoryName'],
                    url=item['url'],
                    description=item['description'],
                    program_language=item['language'],
                    lang='en',  # TODO Determine language with AI based on the title and description
                    total_stars=item['totalStars'],
                    forks=item['forks'],
                    new_stars=item['starsSince'],
                    periodicity=item['since'],
                    tags=self.tags,
                    source_name='GitHub Trends',
                    source_url=self.github_url,
                    contributors=output
                )
                result.append(project)
        return result


def main():
    load_dotenv()
    github_collector = GithubCollector()
    data = github_collector.run()
    if data:
        print(data)


if __name__ == "__main__":
    main()
