from datetime import datetime
from typing import Union, Optional, ClassVar
from ai_datahive.models import ContentBaseModel
from pydantic import HttpUrl, field_validator
import base64


class Media(ContentBaseModel):
    VALID_MEDIA_TYPES: ClassVar[list[str]] = ['image', 'video', 'audio', 'text', 'pdf']
    media_url: Optional[HttpUrl] = None
    media_b64_content: Optional[str] = None
    media_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    likes: int = 0
    hearts: int = 0
    prompt: Optional[str] = None
    model: Optional[str] = None
    author: Optional[str] = None
    # media_reference_id: Optional[Union['Media', str]] = None  # TODO To low level, should reference another media object
    media_created_at: Union[datetime, str]

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }

    @field_validator('media_b64_content')
    def check_base64_content(cls, v: str) -> Union[str, None]:
        if v is None:
            return v
        try:
            base64.b64decode(v)
            return v
        except ValueError:
            raise ValueError('media_b64_content must be base64 encoded')

    @field_validator('media_type')
    def check_media_type(cls, v: str) -> str:
        if v not in Media.VALID_MEDIA_TYPES:
            raise ValueError('media_type must be one of image, audio, video')
        return v

    @field_validator('title', 'description', 'author', mode='after')
    def check_strings(cls, v: str) -> Union[str, None]:
        if v is not None and not isinstance(v, str):
            raise ValueError('Field must be a string')
        return v

    @field_validator('likes', 'hearts', mode='after')
    def check_integers(cls, v: int) -> int:
        if not isinstance(v, int):
            raise ValueError('Field must be an integer')
        return v

    @field_validator('media_created_at', mode='before')
    def parse_image_created_at(cls, v: Union[datetime, str]) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('image_created_at must be a valid datetime string or a datetime object')
        elif not isinstance(v, datetime):
            raise ValueError('image_created_at must be a datetime object')
        return v
