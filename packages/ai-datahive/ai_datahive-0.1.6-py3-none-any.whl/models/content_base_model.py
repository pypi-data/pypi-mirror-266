from ai_datahive.models.base_model import DataHiveBaseModel

from pydantic import field_validator


class ContentBaseModel(DataHiveBaseModel):
    creator: str
    source: str
    version: int = 0
    tags: str

    @field_validator('creator', mode='after')
    def check_strings(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError('Field must be a string')
        return v
