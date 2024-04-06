from ai_datahive.dao.base_dao import BaseDAO


class DataService:
    def __init__(self, dao: BaseDAO):
        self.dao = dao

    # Beispiel: Hinzufügen einer neuen Entität
    def add_entity(self, entity):
        return self.dao.create(entity)

    # Füge hier weitere Geschäftslogiken hinzu

