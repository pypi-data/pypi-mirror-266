from typing import Optional
from ai_datahive.models.base_model import DataHiveBaseModel

from pydantic import HttpUrl, field_validator


class ContentBaseModel(DataHiveBaseModel):
    creator: str
    source_name: str
    source_url: Optional[HttpUrl] = None
    version: int = 0
    lang: str = 'en' # ISO 639-1
    tags: str

    @field_validator('creator', mode='after')
    def check_strings(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError('Field must be a string')
        return v
