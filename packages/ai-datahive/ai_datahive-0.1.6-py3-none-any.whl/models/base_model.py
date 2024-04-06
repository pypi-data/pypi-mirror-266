from typing import Union, Optional
from dataclasses import field
from datetime import datetime
from pydantic import BaseModel


class DataHiveBaseModel(BaseModel):
    id: Optional[Union[str, int]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
