

class BaseAIVisionService:

    def raw_vision_response(self, system_prompt, user_prompt, image_url):
        raise NotImplementedError

    def vision_response(self, system_prompt, user_prompt, image_url):
        raise NotImplementedError

    def switch_vision_model(self, model_name):
        raise NotImplementedError
