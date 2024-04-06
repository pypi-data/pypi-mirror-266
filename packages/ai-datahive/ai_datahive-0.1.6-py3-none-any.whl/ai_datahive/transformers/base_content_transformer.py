import os
import inspect
from typing import Union, Collection, List

from datetime import timedelta
from string import Template
from ai_datahive.utils.text_helper import escape_html

from ai_datahive.transformers.models import Content
from ai_datahive.utils import datetime_helper


class BaseContentTransformer:
    def __init__(self, creator, template_file_name, language, run_interval: timedelta = timedelta(days=1)):
        from ai_datahive.utils.dao_factory import get_dao
        self.dao = get_dao()
        self.language = language
        self.creator = creator
        self.run_interval = run_interval
        caller_file = inspect.getfile(self.__class__)
        caller_dir = os.path.dirname(caller_file)
        template_file_path = os.path.join(caller_dir, 'templates', template_file_name)
        if os.path.exists(template_file_path):
            self.template_path = template_file_path
        elif os.path.exists(os.path.join(os.path.dirname(__file__), 'templates', template_file_name)):
            self.template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)
        else:
            self.template_path = os.path.join('templates', template_file_name)

    def save(self, content: Union[Content, Collection[Content]]):
        if isinstance(content, Collection):
            results = [self.dao.create(c) for c in content]
            return results
        else:
            result = self.dao.create(content)
            return result

    def create_content(self, template_data):
        template_data = {k: escape_html(v) for k, v in template_data.items()}

        with open(self.template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        template = Template(template_content)
        return template.safe_substitute(template_data)

    def retrieve(self):
        raise NotImplementedError

    def transform(self, data) -> List[Content]:
        raise NotImplementedError

    def run(self):
        is_due = datetime_helper.is_due(content_type=Content, creator=self.creator,
                                        run_interval=self.run_interval)
        if is_due:
            # get top image
            # check if top image was already top image
            # if yes try next top image until three tries
            # If all already top images write a message with the first one to say it is again the winner. in a row.
            entities = self.retrieve()
            content = self.transform(entities)
            return self.save(content)
