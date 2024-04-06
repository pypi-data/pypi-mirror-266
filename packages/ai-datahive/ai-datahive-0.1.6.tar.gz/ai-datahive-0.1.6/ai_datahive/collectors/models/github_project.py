from ai_datahive.models import ContentBaseModel

from typing import Optional, ClassVar
from pydantic import HttpUrl, Field, field_validator


class GithubProject(ContentBaseModel):
    VALID_PERIODICITY: ClassVar[list[str]] = ['daily', 'weekly', 'monthly']

    rank: int
    username: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    url: HttpUrl
    description: Optional[str] = None
    program_language: Optional[str] = Field(None, max_length=255)
    total_stars: Optional[int] = None
    forks: Optional[int] = None
    new_stars: Optional[int] = None
    periodicity: str = Field(..., max_length=50)
    contributors: Optional[str] = None

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v)
        }

    @field_validator('periodicity')
    def check_periodicity(cls, v: str) -> str:
        if v not in cls.VALID_PERIODICITY:
            raise ValueError(f"since must be one of {cls.VALID_PERIODICITY}")
        return v
