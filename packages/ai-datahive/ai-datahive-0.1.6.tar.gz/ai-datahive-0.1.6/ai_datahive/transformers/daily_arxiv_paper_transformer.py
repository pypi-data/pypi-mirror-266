from typing import List

from ai_datahive.utils.datetime_helper import today_as_start_and_enddate_str

from ai_datahive.transformers import BaseContentTransformer

from ai_datahive.collectors.models import ResearchPaper
from ai_datahive.transformers.models import Content

from ai_datahive.services import OpenAIService, PromptService


class DailyArxivPaperTransformer(BaseContentTransformer):
    def __init__(self, creator='DailyArxivPaperTransformer', template_file_name='daily_arxiv_paper_template.html',
                 language='de'):

        self.ps = PromptService()
        self.oais = OpenAIService()

        super().__init__(creator=creator, template_file_name=template_file_name, language=language)

    def retrieve(self) -> List[ResearchPaper]:
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "ArxivCollector"], ['created_at', 'between', start_date_str, end_date_str]]
        papers = self.dao.read(ResearchPaper, filters, limit=3, order_by='created_at')
        return papers

    def transform(self, papers: list[ResearchPaper]) -> List[Content]:
        result = []

        for paper in papers:
            paper_language = paper.lang

            system_msg = self.ps.create_summarize_system_prompt()
            if self.language != paper_language:
                system_msg += self.ps.create_translate_system_prompt(language=self.language)

            self.oais.switch_text_model('gpt-3.5-turbo')
            abstract = self.oais.chat_response(system_msg, paper.abstract)
            self.oais.switch_to_default_text_model()

            template_data = {
                'title': paper.title,
                'abstract': abstract,
                'authors': paper.authors,
                'date': paper.created_at.strftime('%d.%m.%Y %H:%M'),
                'url': paper.paper_url
            }
            str_content = self.create_content(template_data)

            content = Content(
                title=paper.title,
                content=str_content,
                reference_url=paper.paper_url,
                reference_type='paper',
                reference_created_at=paper.created_at,
                source_name=paper.source_name,
                source_url=paper.source_url,
                lang=self.language,
                creator=self.creator,
                tags=paper.tags,
            )
            result.append(content)
        return result


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = DailyArxivPaperTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
