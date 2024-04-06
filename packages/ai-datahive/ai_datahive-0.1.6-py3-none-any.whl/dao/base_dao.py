from typing import Any, Union, Type, List, Tuple, TypeVar
from datetime import datetime

from ai_datahive.models import DataHiveBaseModel

#TODO get rid of Any - it is str or List with another str elements.
Filter = Union[Tuple[str, Any], Tuple[str, Any, Any], Tuple[str, Any, Any, Any], List[Any]]
T = TypeVar('T', bound=DataHiveBaseModel)

class BaseDAO:
    def create(self, entity: DataHiveBaseModel) -> DataHiveBaseModel:
        raise NotImplementedError

    def read(self, entity: Type[T], filters: Filter = None, limit=None, order_by=None,
             order_dir='asc') -> list[T]:
        raise NotImplementedError

    def update(self, entity: DataHiveBaseModel, id=None) -> DataHiveBaseModel:
        raise NotImplementedError

    def delete(self, entity: DataHiveBaseModel, id=None):
        raise NotImplementedError

    def get_latest_entity_date(self, entity: Type[DataHiveBaseModel], creator_name: str) -> Union[datetime, None]:
        entity = self.read(entity, filters=[['creator', creator_name]], order_by='created_at', order_dir='desc',
                             limit=1)

        if entity:
            entity = entity[0]
            return entity.created_at
        else:
            return None
