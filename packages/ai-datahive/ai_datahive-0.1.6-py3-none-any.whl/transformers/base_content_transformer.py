import os
from typing import Union, Collection

from string import Template
from ai_datahive.utils import escape_html

from ai_datahive.transformers import Content


class BaseContentTransformer:
    def __init__(self, creator_name, template_file_name, language):
        from ai_datahive.utils.dao_factory import dao_factory
        self.dao = dao_factory()
        self.language = language
        self.creator_name = creator_name
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)

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

    def transform(self, data):
        raise NotImplementedError

    def run(self):
        # get top image
        # check if top image was already top image
        # if yes try next top image until three tries
        # If all already top images write a message with the first one to say it is again the winner. in a row.
        entities = self.retrieve()
        content = self.transform(entities)
        self.save(content)
