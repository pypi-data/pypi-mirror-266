from typing import List

from ai_datahive.collectors.models import GithubProject
from ai_datahive.transformers import BaseContentTransformer
from ai_datahive.transformers.models import Content

from ai_datahive.services import AIBackedTranslationService

from ai_datahive.utils.datetime_helper import get_start_and_end_times_based_on_interval
from ai_datahive.utils.text_helper import replace_numbers_with_emojis


class DailyTrendingGithubProjectTransformer(BaseContentTransformer):
    def __init__(self, creator='DailyTrendingGithubProjectTransformer',
                 template_file_name='github_loader_trending_template.html', language='de'):

        self.ts = AIBackedTranslationService()

        super().__init__(creator=creator, template_file_name=template_file_name, language=language)

    def retrieve(self) -> List[GithubProject]:
        # start_date_str, end_date_str = today_as_start_and_enddate_str()
        start_date_str, end_date_str = get_start_and_end_times_based_on_interval(self.run_interval)

        filters = [["creator", "GithubCollector"], ['created_at', 'between', start_date_str, end_date_str]]
        projects = self.dao.read(GithubProject, filters, limit=3, order_by='created_at')
        return projects

    def transform(self, projects: list[GithubProject]) -> List[Content]:
        result = []

        for project in projects:
            project_language = project.lang
            if self.language != project_language:
                translated_description = self.ts.translate(project.description, self.language)
                project.description = translated_description

            template_data = {
                'rank': replace_numbers_with_emojis(str(project.rank)),
                'username': project.username,
                'repositoryName': project.name,
                'url': project.url,
                'description': project.description,
                'stars': project.total_stars,
                'starsSince': project.new_stars,
                'forks': project.forks,
            }
            str_content = self.create_content(template_data)

            content = Content(
                title=project.name,
                content=str_content,
                reference_url=project.url,
                reference_type='github_project',
                reference_created_at=project.created_at,
                source_name=project.source_name,
                source_url=project.source_url,
                lang=self.language,
                creator=self.creator,
                tags=project.tags,
            )
            result.append(content)
        return result


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = DailyTrendingGithubProjectTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
