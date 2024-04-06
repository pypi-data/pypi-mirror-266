from typing import Optional, Union
from datetime import datetime

from ai_datahive.models import DataHiveBaseModel

from pydantic import HttpUrl


class TelegramMessage(DataHiveBaseModel):
    telegram_group_topic_fk: str
    content: Optional[str] = None
    media_content: Optional[str] = None
    media_url: Optional[HttpUrl] = None
    media_type: Optional[str] = None
    creator: str
    scheduled_for: Optional[Union[datetime, str]] = None
    sent_at: Optional[Union[datetime, str]] = None
    status: str
