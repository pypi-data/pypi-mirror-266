from datetime import datetime
from typing import Union, Optional
from ai_datahive.models import ContentBaseModel
from pydantic import HttpUrl


class ResearchPaper(ContentBaseModel):
    title: str
    abstract: Optional[str] = None
    source_id: str
    authors: str
    license: Optional[str] = None
    paper_url: Optional[HttpUrl] = None
    code_url: Optional[HttpUrl] = None
    media_url: Optional[HttpUrl] = None
    paper_submitted_at: Union[datetime, str]
