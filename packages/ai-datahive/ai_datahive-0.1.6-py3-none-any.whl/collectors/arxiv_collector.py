import os
from typing import List

from dotenv import load_dotenv
from datetime import datetime, timezone

from ai_datahive.collectors import BaseCollector
import ai_datahive.collectors.utils.arxiv_helper as ah

from ai_datahive.utils import to_periodic_format
from ai_datahive.collectors import ResearchPaper


class ArxivCollector(BaseCollector):

    VALID_PERIODS = ['Day']

    def __init__(self, creator_name='ArxivCollector', arxiv_category='cs.AI', period='Day', tags=None, limit=3):
        self.validate_parameters(arxiv_category, period)

        self.creator_name = creator_name
        self.limit = limit
        self.arxiv_category = arxiv_category
        self.period = period

        if tags is None:
            self.tags = self.build_tags(arxiv_category, period)
        else:
            self.tags = tags

        super().__init__(creator_name=self.creator_name, content_type=ResearchPaper)

    def validate_parameters(self, arxiv_category, period) -> None:
        if arxiv_category not in ah.ALL_CATEGORIES:
            raise ValueError(f"category must be one of {ah.ALL_CATEGORIES}")
        if period not in self.VALID_PERIODS:
            raise ValueError(f"period must be one of {self.VALID_PERIODS}")

    def build_tags(self, arxiv_category, period) -> str:
        tags = 'arxiv, '
        tags += arxiv_category.lower() + ', '
        tags += to_periodic_format(period) + ', '

        tags = tags.rstrip(', ')
        return tags

    def retrieve(self) -> List[ResearchPaper]:
        entries = ah.do_today_search(self.arxiv_category, self.limit)
        papers = self.convert_to_research_paper_entities(entries)
        return papers

    def convert_to_research_paper_entities(self, data) -> List[ResearchPaper]:
        result = []
        if data:
            for item in data:
                if 'Remaining Information' in item['title']:
                    # TODO make here a news item??
                    #paper = ResearchPaper(
                    #    creator=self.creator_name,
                    #    title=item['title'],
                    #    description=item['description'],
                    #    tags=self.tags + ', count',
                    #    authors=self.creator_name,
                    #    source='Arxiv',
                        # TODO rework function call
                    #    reference_url=ah.search_day_submissions(self.arxiv_category, os.getenv('ARXIV_RSS_LINK'))
                    #)
                    pass
                else:
                    now = datetime.now(timezone.utc)
                    paper = ResearchPaper(
                        title=item['title'],
                        abstract=item['description'],
                        source_id=item['guid'],
                        authors=item['authors'],
                        license=item['rights'],
                        source='Arxiv',
                        creator=self.creator_name,
                        tags=self.tags,
                        paper_submitted_at=now,
                        paper_url=item['link'],
                        # TODO rework function call
                        reference_url=ah.search_day_submissions(self.arxiv_category, os.getenv('ARXIV_RSS_LINK'))
                    )
                    result.append(paper)
        return result


def main():
    load_dotenv()
    arxiv_collector = ArxivCollector()
    data = arxiv_collector.run()
    #result = arxiv_collector.save(data)
    print(data)
    #media = civitai_collector.convert_to_media(data)

    #print(media)


if __name__ == "__main__":
    main()
