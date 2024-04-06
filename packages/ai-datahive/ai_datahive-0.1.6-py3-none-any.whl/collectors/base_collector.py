from typing import Type, Union
from collections.abc import Collection

from datetime import datetime, timezone, timedelta

from ai_datahive.models import ContentBaseModel


class BaseCollector:

    def __init__(self, content_type: Type[ContentBaseModel], creator_name: str,
                 run_interval: timedelta = timedelta(days=1)):
        from ai_datahive.utils.dao_factory import dao_factory

        self.creator_name = creator_name
        self.content_type = content_type
        self.run_interval = run_interval

        self.dao = dao_factory()

    def get_latest_message_date(self):
        # Get date from the latest message to the telegram table - using topic / reporter
        result = self.dao.get_latest_entity_date(self.content_type, self.creator_name)
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

    def is_due(self):
        latest_entity_date = self.get_latest_message_date()
        if latest_entity_date is None:
            return True

        latest_entity_date = latest_entity_date.astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = now - latest_entity_date

        if time_diff < self.run_interval:
            total_seconds = time_diff.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            print(f"Weniger als 24 Stunden seit der letzten Nachricht vergangen: "
                  f"Vergangen bisher: {hours:02d}:{minutes:02d}")
            return False
        return True

    def run(self):
        if self.is_due():
            try:
                data = self.retrieve()
                self.save(data=data)
            except Exception as e:
                print(f"Error in {self.creator_name}: {e}")
