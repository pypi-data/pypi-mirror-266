import os
import openai

from ai_datahive.services import BaseLLMService, BaseAIVisionService


class OpenAIService(BaseLLMService, BaseAIVisionService):

    ALLOWED_TEXT_MODELS = ['gpt-4-1106-preview', 'gpt-3.5-turbo']
    ALLOWED_VISION_MODELS = ['gpt-4-vision-preview']

    def __init__(self, openai_key=None, text_model='gpt-4-1106-preview', vision_model='gpt-4-vision-preview'):
        openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        self._openai_client = openai.OpenAI(api_key=openai_key)
        self.text_model = text_model
        self.vision_model = vision_model

    def switch_text_model(self, model_name):
        self.text_model = model_name

    def switch_to_default_text_model(self):
        self.text_model = 'gpt-4-1106-preview'

    def switch_vision_model(self, vision_model_name):
        self.vision_model = vision_model_name

    def raw_chat_response(self, system_prompt, user_prompt):
        response = self._openai_client.chat.completions.create(
            model=self.text_model,
            messages=[
                {
                    "role": "system", "content": f"{system_prompt}",
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}",
                }
            ],
            max_tokens=3000,
            temperature=0.7
        )
        return response.choices[0]

    def chat_response(self, system_prompt, user_prompt):
        response = self.raw_chat_response(system_prompt, user_prompt)
        return response.message.content

    def raw_vision_response(self, system_prompt, user_prompt, image_url):
        response = self._openai_client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "system", "content": f"{system_prompt}"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{user_prompt}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image_url}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=3000,
            temperature=0.7,
        )
        return response.choices[0]

    def vision_response(self, system_prompt, user_prompt, image_url):
        response = self.raw_vision_response(system_prompt, user_prompt, image_url)
        return response.message.content
