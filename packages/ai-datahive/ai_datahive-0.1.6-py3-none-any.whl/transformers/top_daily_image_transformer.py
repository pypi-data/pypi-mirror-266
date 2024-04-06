import os

from string import Template

from ai_datahive.utils import escape_html
from ai_datahive.utils import today_as_start_and_enddate_str

from ai_datahive.collectors import Media
from ai_datahive.transformers import Content


class TopDailyImageTransformer:
    def __init__(self, template_file_name='top_daily_image_template.html', language='de'):
        from ai_datahive.utils.dao_factory import dao_factory
        self.creator = 'TopDailyImage'
        self.dao = dao_factory()

        self.language = language
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)

    def retrieve(self):
        start_date_str, end_date_str = today_as_start_and_enddate_str()

        filters = [["creator", "CivitAIDailyTopImage"], ['created_at', 'between', start_date_str, end_date_str]]
        media = self.dao.read(Media, filters, limit=1, order_by='likes')
        return media[0] if media else None

    def transform(self, topdailyimage: Media) -> Content:
        if topdailyimage:
            template_data = {
                'creator': topdailyimage.source,
                'media_url': topdailyimage.media_url,
                'likes': topdailyimage.likes,
                'hearts': topdailyimage.hearts,
                'prompt': topdailyimage.prompt,
                'model': topdailyimage.model,
                'author': topdailyimage.author,
                'created_at': topdailyimage.media_created_at,
            }
            str_content = self.create_content(template_data)

            content = Content(
                creator=self.creator,
                tags=topdailyimage.tags,
                title=f'Das Topbild des Tages von {topdailyimage.source}:',
                content=str_content,
                media_url=topdailyimage.media_url,
                media_type='image',
                media_created_at=topdailyimage.media_created_at,
                source=topdailyimage.source,
                language=self.language
            )

            return content

    def save(self, content: Content):
        result = self.dao.create(content)
        return result

    def create_content(self, template_data):
        template_data = {k: escape_html(v) for k, v in template_data.items()}

        with open(self.template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()

        template = Template(template_content)
        return template.safe_substitute(template_data)

    def run(self):
        # get top image
        # check if top image was already top image
        # if yes try next top image until three tries
        # If all already top images write a message with the first one to say it is again the winner. in a row.
        media = self.retrieve()
        content = self.transform(media)
        self.save(content)


def main():
    from dotenv import load_dotenv
    load_dotenv()

    transformer = TopDailyImageTransformer()
    transformer.run()


if __name__ == "__main__":
    main()
