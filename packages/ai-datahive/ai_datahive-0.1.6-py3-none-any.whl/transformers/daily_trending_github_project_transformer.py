from typing import List

from ai_datahive.collectors import GithubProject
from ai_datahive.transformers import BaseContentTransformer
from ai_datahive.transformers import Content

from ai_datahive.services import AIBackedTranslationService

from ai_datahive.utils import today_as_start_and_enddate_str
from ai_datahive.utils import replace_numbers_with_emojis

class DailyTrendingGithubProjectTransformer(BaseContentTransformer):
    def __init__(self, creator_name='DailyTrendingGithubProjects',
                 template_file_name='github_loader_trending_template.html', language='de'):
        from ai_datahive.utils.dao_factory import dao_factory
        self.dao = dao_factory()

        self.ts = AIBackedTranslationService()

        super().__init__(creator_name=creator_name, template_file_name=template_file_name, language=language)

    def retrieve(self) -> List[GithubProject]:
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "GithubCollector"], ['created_at', 'between', start_date_str, end_date_str]]
        projects = self.dao.read(GithubProject, filters, limit=3, order_by='created_at')
        return projects

    def transform(self, projects: list[GithubProject]) -> List[Content]:
        # TODO make a language system. Getting the language from Paper and Check language in this transformer
        # TODO If different make a translation
        # Hardcoded for now
        project_language = 'en'
        result = []

        for project in projects:
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
                source=project.source,
                language=self.language,
                creator=self.creator_name,
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
