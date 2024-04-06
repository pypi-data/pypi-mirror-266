from typing import Optional, Type, Union
from collections.abc import Collection

from datetime import timedelta

from ai_datahive.models import ContentBaseModel
from ai_datahive.utils import datetime_helper


class BaseCollector:

    def __init__(self, content_type: Optional[Type[ContentBaseModel]], creator: str,
                 run_interval: timedelta = timedelta(days=1)):
        from ai_datahive.utils.dao_factory import get_dao

        self.creator = creator
        self.content_type = content_type
        self.run_interval = run_interval

        self.dao = get_dao()

    def get_latest_message_date(self):
        # Get date from the latest message to the telegram table - using topic / reporter
        if self.content_type is None:
            raise NotImplementedError('If no content_type is defined, you have to implement this method.')

        result = self.dao.get_latest_entity_date(self.content_type, self.creator)

        return result

    def retrieve(self) -> Union[ContentBaseModel, Collection[ContentBaseModel]]:
        # Get data from the source
        raise NotImplementedError

    def save(self, data: Union[ContentBaseModel, Collection[ContentBaseModel]]):
        if isinstance(data, Collection):
            result = []
            for item in data:
                result.append(self.dao.create(item))
            return result
        else:
            return self.dao.create(data)

    def run(self):
        is_due = datetime_helper.is_due(content_type=self.content_type, creator=self.creator,
                                        run_interval=self.run_interval)
        if is_due:
            try:
                data = self.retrieve()
                return self.save(data=data)
            except Exception as e:
                print(f"Error in {self.creator}: {e}")
