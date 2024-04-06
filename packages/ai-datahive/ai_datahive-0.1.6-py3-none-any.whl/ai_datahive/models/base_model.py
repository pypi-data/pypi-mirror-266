from typing import Union, Optional
from dataclasses import field
from datetime import datetime, timezone
from pydantic import BaseModel


class DataHiveBaseModel(BaseModel):
    id: Optional[Union[str, int]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
