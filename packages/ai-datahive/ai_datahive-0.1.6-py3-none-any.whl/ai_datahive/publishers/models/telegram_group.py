from ai_datahive.models import DataHiveBaseModel


class TelegramGroup(DataHiveBaseModel):
    id: str
    telegram_group_name: str
    telegram_group_chat_id: int
