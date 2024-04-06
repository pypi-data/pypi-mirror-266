from ai_datahive.utils import today_as_start_and_enddate_str

from ai_datahive.transformers import BaseContentTransformer

from ai_datahive.collectors import Media
from ai_datahive.transformers import Content

from ai_datahive.services import OpenAIService, PromptService, AIBackedTranslationService


class TopDailyImageCritiqueTransformer(BaseContentTransformer):
    def __init__(self, creator_name='DailyImageCritiqueJS', template_file_name='top_daily_image_critique_template.html',
                 language='de'):
        from ai_datahive.utils.dao_factory import dao_factory
        self.dao = dao_factory()

        self.ps = PromptService()
        self.oais = OpenAIService()
        self.ts = AIBackedTranslationService()

        super().__init__(creator_name=creator_name, template_file_name=template_file_name, language=language)

    def retrieve(self) -> Media:
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "CivitAIDailyTopImage"], ['created_at', 'between', start_date_str, end_date_str]]
        media = self.dao.read(Media, filters, limit=1, order_by='likes')
        return media[0] if media else None

    def transform(self, topdailyimage: Media) -> Content:

        if topdailyimage:
            system_prompt = self.ps.create_system_prompt_from_file('js_style_image_critique_prompt.txt')

            user_prompt = f"Prompt: {topdailyimage.prompt}\nartist: {topdailyimage.author}"
            critique = self.oais.vision_response(system_prompt=system_prompt, user_prompt=user_prompt,
                                                 image_url=topdailyimage.media_url)
            if self.language != 'en':
                critique = self.ts.translate(critique, self.language)

            template_data = {
                'critique': critique,
                'author': topdailyimage.author,
                'created_at': topdailyimage.media_created_at,
                'media_url': topdailyimage.media_url,
            }
            str_content = self.create_content(template_data)

            content = Content(
                creator=self.creator_name,
                tags=topdailyimage.tags+', critique, JS style',
                title=f'Die Bildkritik mit Saltz',
                content=str_content,
                media_url=topdailyimage.media_url,
                media_type='image',
                media_created_at=topdailyimage.media_created_at,
                source=topdailyimage.source,
                language=self.language
            )
            return content


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = TopDailyImageCritiqueTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
