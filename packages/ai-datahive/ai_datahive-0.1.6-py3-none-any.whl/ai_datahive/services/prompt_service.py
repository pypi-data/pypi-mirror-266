import os

from string import Template


class PromptService:

    def __init__(self, prompt_path=None):
        if prompt_path:
            self.template_path = prompt_path
        else:
            self.template_path = os.path.join(os.path.dirname(__file__), 'prompts')

    def _create_prompt_file_path(self, prompt_file):
        return os.path.join(self.template_path, prompt_file)

    def _create_prompt_template(self, prompt_file=None, prompt=None):
        if not prompt_file and not prompt:
            ValueError('No prompt file or prompt string specified.')

        if not prompt:
            prompt = self.create_system_prompt_from_file(prompt_file)
        prompt_template = Template(prompt)

        return prompt_template

    def _create_prompt(self, prompt_template, prompt_data=None):
        if not prompt_data:
            prompt_data = {}

        return prompt_template.safe_substitute(prompt_data)

    def create_system_prompt_from_file(self, prompt_file):
        prompt_file_path = self._create_prompt_file_path(prompt_file)
        with open(prompt_file_path, 'r') as f:
            prompt = f.read()
        return prompt

    def create_translate_system_prompt(self, language=None, prompt_file='translate_prompt.txt', prompt=None):
        if not language:
            ValueError('No target language for the translation specified.')
        else:
            # read prompt from file relative directory prompts/translate_prompt.txt
            prompt_template = self._create_prompt_template(prompt_file, prompt)
            prompt_data = {'lang': language}
            prompt = self._create_prompt(prompt_template, prompt_data)

            return prompt

    def create_summarize_system_prompt(self, prompt_file='summarize_prompt.txt', prompt=None):
        prompt = self.create_system_prompt_from_file(prompt_file) if not prompt else prompt
        return prompt
