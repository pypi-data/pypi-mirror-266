import os
import re
import inflect

from datetime import datetime
from typing import Annotated, get_origin, get_args, Union, Type, List

from ai_datahive.dao import BaseDAO, T, Filter
from ai_datahive.transformers.models import Content
from supabase import create_client, Client

from pydantic_core import Url


class SupabaseDAO(BaseDAO):

    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_api_key = os.getenv('SUPABASE_KEY')

        self.supabase_client: Client = create_client(supabase_url, supabase_api_key)

    def create(self, entity: T) -> T:
        table_name = self.table_name_from_model(type(entity))
        row_data = self._model_instance_to_row(entity)
        del row_data['id']
        response = self.supabase_client.table(table_name).insert(row_data).execute()
        data = response.data
        return self._row_to_model_instance(data[0], type(entity))

    def read(self, entity: Type[T], filters=None, limit=None, order_by=None, order_dir='asc') -> (
            Union)[Type[T], list[Type[T]]]:
        table_name = self.table_name_from_model(entity)
        result = self.supabase_client.table(table_name).select("*")

        if filters is not None:
            query_filters = self.convert_filters_to_query(filters)
            for query in query_filters:
                # Trennen des Feldnamens vom Rest der Bedingung
                field_operator_criteria = query.split('=', 1)
                if len(field_operator_criteria) == 2:
                    field, operator_criteria = field_operator_criteria
                    # Nun müssen wir operator_criteria in Operator und Kriterium aufteilen
                    operator, criteria = operator_criteria.split('.', 1)
                    result = result.filter(field, operator, criteria)
                else:
                    # Fallback, falls das Format ungültig ist
                    print(f"Fehler: Filterformat ist ungültig: '{query}'")

            # Order By und Richtung anwenden, wenn spezifiziert
        if order_by is not None:
            result = result.order(order_by, desc=(order_dir == 'desc'))

            # Limit anwenden, wenn spezifiziert
        if limit is not None:
            result = result.limit(limit)

        return [self._row_to_model_instance(row, entity) for row in result.execute().data]

    def update(self, entity: T, id=None):
        table_name = self.table_name_from_model(type(entity))
        row_data = self._model_instance_to_row(entity)
        if id is None:
            id = entity.id

        self.supabase_client.table(table_name).update(row_data).eq('id', id).execute()

    def delete(self, entity: T, id=None):
        # Implementiere die Methode unter Verwendung von Supabase
        pass

    def is_of_type(self, typ, check) -> bool:
        """Prüft, ob `typ` dem `check` Typ entspricht, auch innerhalb von Union- und Optional-Typen."""
        origin = get_origin(typ)
        if origin is Union:
            return any(self.is_of_type(arg, check) for arg in get_args(typ))
        elif origin is Annotated:
            # Prüfe den Basistyp in Annotated-Typen
            base_type = get_args(typ)[0]
            return self.is_of_type(base_type, check)
        elif origin:
            # Für andere generische Typen (wie List, Dict usw.)
            return False
        return isinstance(typ, type) and issubclass(typ, check)

    def convert_row_to_model_value(self, expected_type, value):
        """Konvertiert einen Wert in den erwarteten Typ, wenn möglich."""
        if value is None:
            return None
        if self.is_of_type(expected_type, datetime):
            return datetime.fromisoformat(value) if isinstance(value, str) else value
        elif self.is_of_type(expected_type, Url):
            # Da HttpUrl ein spezialisierter Url-Typ ist, prüfen wir auf Url oder UrlStr
            return str(value)
            # Ergänzen Sie hier Konvertierungen für weitere spezielle Typen
        return value

    def convert_model_to_row_value(self, field_type, value):
        """Konvertiert einen Wert in den erwarteten Typ, wenn möglich."""
        if value is None:
            return None
        if self.is_of_type(field_type, datetime) and not isinstance(value, str):
            return value.isoformat()
        elif self.is_of_type(field_type, Url):
            return str(value)
            # Ergänzen Sie hier Konvertierungen für weitere spezielle Typen
        return value

    def _row_to_model_instance(self, row: dict, model: Type[T]) -> T:
        init_values = {}
        for field_name, field_info in model.__fields__.items():
            field_value = row.get(field_name)
            field_type = field_info.annotation
            converted_value = self.convert_row_to_model_value(field_type, field_value)
            init_values[field_name] = converted_value
        return model(**init_values)

    def _model_instance_to_row(self, model_instance: T) -> dict:
        row_data = {}
        for field_name, field_info in model_instance.__fields__.items():
            value = getattr(model_instance, field_name, None)
            field_type = field_info.annotation
            row_data[field_name] = self.convert_model_to_row_value(field_type, value)
        return row_data

    def table_name_from_model(self, model: Type[T]) -> str:
        inflect.def_classical["names"] = False
        p = inflect.engine()
        model_name = model.__name__
        table_name_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', model_name).lower()

        # TODO find a better way to handle pluralization
        if 'media' in table_name_snake_case:
            table_name_plural = 'media'
        elif 'content' in table_name_snake_case:
            table_name_plural = 'content'
        else:
            table_name_plural = p.plural_noun(table_name_snake_case)

        table_name = f"t_{table_name_plural}"
        return table_name

    def convert_filters_to_query(self, filters: List[Filter]) -> List[str]:
        query_filters = []

        def process_filter(filter: Filter):
            if isinstance(filter, list) and filter[0] == 'or':
                # Process an 'or' condition
                or_filters = [process_filter(f).replace('=', '.') for f in filter[1:]]
                return f"or=({','.join(or_filters)})"
            elif len(filter) == 2:
                # Standardfall: Feld und Wert (impliziert "=" Operator)
                field, value = filter
                return f"{field}=eq.{value}"
            elif len(filter) == 3:
                # Spezialfall: Feld, Operator, Wert
                field, operator, value = filter
                return f"{field}={operator}.{value}"
            elif len(filter) == 4:
                # Erweiterter Fall für spezielle Logiken wie "between"
                field, op_start, start_value, end_value = filter
                if op_start.lower() == "between":
                    return [f"{field}=gte.{start_value}", f"{field}=lte.{end_value}"]

        for filter in filters:
            result = process_filter(filter)
            if isinstance(result, list):
                query_filters.extend(result)
            else:
                query_filters.append(result)

        return query_filters


def main():
    from dotenv import load_dotenv
    from ai_datahive.publishers.models import TelegramMessage

    load_dotenv()

    dao = SupabaseDAO()
    #print(dao.read(TelegramMessage, limit=1))

    content = Content(
        title="Test",
        content="Test",
        creator="Test",
        tags="Test",
        source="Test",
        language="de"
    )

    #print(dao.create(content))
    now = datetime.utcnow()
    tmsgs = dao.read(TelegramMessage, filters=[['or', ["scheduled_for", "lte", now.isoformat()], ["scheduled_for", "is", "null"]], ["sent_at", "is", "null"]],
                     order_by="created_at")
    print(tmsgs)


if __name__ == "__main__":
    main()
