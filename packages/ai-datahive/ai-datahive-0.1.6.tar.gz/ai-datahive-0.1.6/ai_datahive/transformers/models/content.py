from typing import Union, Optional
from ai_datahive.models import ContentBaseModel
from pydantic import HttpUrl
from datetime import datetime


class Content(ContentBaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_url: Optional[HttpUrl] = None
    media_type: Optional[str] = None
    media_created_at: Optional[Union[datetime, str]] = None
    reference_url: Optional[HttpUrl] = None
    reference_type: Optional[str] = None
    reference_created_at: Optional[Union[datetime, str]] = None
    scheduled_for: Optional[Union[datetime, str]] = None        
