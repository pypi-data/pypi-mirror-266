import os
from ai_datahive.services import BaseLLMService, BaseAIVisionService, OpenAIService


def load_llm_service(key) -> BaseLLMService:
    llm_service = os.getenv(key, 'openai')
    if llm_service == 'openai':
        return OpenAIService()
    else:
        return OpenAIService()


def load_ai_vision_service(key) -> BaseAIVisionService:
    ai_vision_service = os.getenv(key, 'openai')
    if ai_vision_service == 'openai':
        return OpenAIService()
    else:
        return OpenAIService()
