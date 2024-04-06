import os

from ai_datahive.utils.datetime_helper import today_as_start_and_enddate_str

from ai_datahive.transformers import BaseContentTransformer
from ai_datahive.collectors.models import Media
from ai_datahive.transformers.models import Content


class TopDailyImageTransformer(BaseContentTransformer):
    def __init__(self, creator='TopDailyImageTransformer', template_file_name='top_daily_image_template.html',
                 language='de'):

        self.creator = creator
        self.language = language
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)

        super().__init__(creator=creator, template_file_name=template_file_name, language=language)

    def retrieve(self):
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "CivitAIDailyTopImage"], ['created_at', 'between', start_date_str, end_date_str]]
        media = self.dao.read(Media, filters, limit=1, order_by='likes')
        return media[0] if media else None

    def transform(self, topdailyimage: Media) -> Content:
        if topdailyimage:
            template_data = {
                'creator': self.creator,
                'media_url': topdailyimage.media_url,
                'likes': topdailyimage.likes,
                'hearts': topdailyimage.hearts,
                'prompt': topdailyimage.prompt,
                'model': topdailyimage.model,
                'author': topdailyimage.author,
                'created_at': topdailyimage.media_created_at.strftime('%d.%m.%Y %H:%M'),
            }
            str_content = self.create_content(template_data)

            content = Content(
                creator=self.creator,
                tags=topdailyimage.tags,
                title=f'Das Topbild des Tages von {topdailyimage.source_name}:',
                content=str_content,
                media_url=topdailyimage.media_url,
                media_type='image',
                media_created_at=topdailyimage.media_created_at,
                source_name=topdailyimage.source_name,
                source_url=topdailyimage.source_url,
                lang=self.language
            )

            return content


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = TopDailyImageTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
