from ai_datahive.services import PromptService, ai_service_factory

class AIBackedTranslationService:
    def __init__(self):
        self.llm_service = ai_service_factory.load_llm_service('TRANSLATION_LLM_SERVICE')
        self.ps = PromptService()

    def translate(self, text, target_language):
        system_msg = self.ps.create_translate_system_prompt(language=target_language)
        translation = self.llm_service.chat_response(system_msg, text)
        return translation
