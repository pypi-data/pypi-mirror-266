from ai_datahive.models import DataHiveBaseModel


class TelegramGroupTopic(DataHiveBaseModel):
    id: str
    telegram_group_fk: str
    telegram_group_topic_name: str
    telegram_group_topic_id: int
