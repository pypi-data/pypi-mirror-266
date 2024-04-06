

# TODO supporting chats with memory
class BaseLLMService:

    def raw_chat_response(self, system_prompt, user_prompt):
        raise NotImplementedError

    def chat_response(self, system_prompt, user_prompt):
        raise NotImplementedError

    def switch_text_model(self, model_name):
        raise NotImplementedError

    def switch_to_default_text_model(self):
        raise NotImplementedError
