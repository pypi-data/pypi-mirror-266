from typing import List

from ai_datahive.utils import today_as_start_and_enddate_str

from ai_datahive.transformers import BaseContentTransformer

from ai_datahive.collectors import ResearchPaper
from ai_datahive.transformers import Content

from ai_datahive.services import OpenAIService, PromptService


class DailyArxivPaperTransformer(BaseContentTransformer):
    def __init__(self, creator_name='DailyArxivPaper', template_file_name='daily_arxiv_paper_template.html', language='de'):
        from ai_datahive.utils.dao_factory import dao_factory
        self.dao = dao_factory()

        self.ps = PromptService()
        self.oais = OpenAIService()

        super().__init__(creator_name=creator_name, template_file_name=template_file_name, language=language)

    def retrieve(self) -> List[ResearchPaper]:
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "ArxivCollector"], ['created_at', 'between', start_date_str, end_date_str]]
        papers = self.dao.read(ResearchPaper, filters, limit=3, order_by='created_at')
        return papers

    def transform(self, papers: list[ResearchPaper]) -> List[Content]:
        # TODO make a language system. Getting the language from Paper and Check language in this transformer
        # TODO If different make a translation
        # Hardcoded for now
        paper_language = 'en'
        result = []

        for paper in papers:
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
                'date': paper.created_at,
                'url': paper.paper_url
            }
            str_content = self.create_content(template_data)

            content = Content(
                title=paper.title,
                content=str_content,
                reference_url=paper.paper_url,
                reference_type='paper',
                reference_created_at=paper.created_at,
                source=paper.source,
                language=self.language,
                creator=self.creator_name,
                tags=paper.tags,
            )
            result.append(content)
        return result

    def run(self):
        # get top image
        # check if top image was already top image
        # if yes try next top image until three tries
        # If all already top images write a message with the first one to say it is again the winner. in a row.
        papers = self.retrieve()
        content = self.transform(papers)
        self.save(content)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = DailyArxivPaperTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
