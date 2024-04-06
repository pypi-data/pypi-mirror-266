import os
from dotenv import load_dotenv
from urllib.parse import urlencode, urljoin

from ai_datahive.collectors import BaseCollector
from ai_datahive.collectors.utils.scraping_helper import get_request_as_json
from ai_datahive.utils.datetime_helper import to_periodic_format

from ai_datahive.collectors.models import Media


class CivitaiCollector(BaseCollector):
    VALID_PERIODS = ['AllTime', 'Year', 'Month', 'Week', 'Day']
    VALID_MEDIA_TYPES = ['image', 'video', 'model']
    VALID_NSFW_LEVELS = ['None', 'Soft', 'Mature', 'X']
    VALID_SORTS = ['Most Reactions', 'Most Buzz', 'Most Comments', 'Most Collected', 'Oldest']

    def __init__(self, creator='CivitaiCollector', media_type='image', period='Day', sort='Most Reactions',
                 nsfw_level='None', tags=None, limit=10):
        self.creator = creator
        self.nsfw_level = nsfw_level
        if tags is None:
            self.tags = self.build_tags(media_type, period, sort, self.nsfw_level)
        else:
            self.tags = tags
        self.limit = limit

        if self.nsfw_level is None:
            self.nsfw_level = 'None'
        self.validate_parameters(media_type, period, self.nsfw_level, sort)

        # TODO Right now, there is no way to determine videos directly from Civitai API
        # START - Workaround as long as there is no way to get videos directly from Civitai
        if media_type == 'video':
            self.media_type = 'image'
        else:
            self.media_type = media_type
        # END - Workaround as long as there is no way to get videos directly from Civitai

        base_url = os.getenv('CIVITAI_API_URL', '')
        self.civitai_url = self.build_url(base_url, media_type, sort, self.nsfw_level, period)

        super().__init__(creator=self.creator, content_type=Media)

    def build_tags(self, media_type, period, sort, nsfw):
        tags = 'civitai, '
        tags += media_type.lower() + ', '
        tags += to_periodic_format(period) + ', '
        tags += sort.lower() + ', '

        if nsfw:
            tags += nsfw.lower() + ', '

        tags = tags.rstrip(', ')
        return tags

    def validate_parameters(self, media_type, period, nsfw, sort):
        if period not in self.VALID_PERIODS:
            raise ValueError(f"period must be one of {self.VALID_PERIODS}")
        if media_type not in self.VALID_MEDIA_TYPES:
            raise ValueError(f"media_type must be one of {self.VALID_MEDIA_TYPES}")
        if nsfw not in self.VALID_NSFW_LEVELS:
            raise ValueError(f"nsfw must be one of {self.VALID_NSFW_LEVELS}")
        if sort not in self.VALID_SORTS:
            raise ValueError(f"sort must be one of {self.VALID_SORTS}")

    def build_url(self, base_url, media_type, sort, nsfw, period):
        api_limit = 100  # Maximum limit for Civitai API
        path = f"{media_type}s"  # Append 's' to make it plural (image -> images, video -> videos, model -> models)
        params = {
            'nsfw': nsfw if nsfw is not None else 'None',
            'limit': api_limit,
            'period': period,
            'sort': sort
        }
        query_string = urlencode({k: v for k, v in params.items() if v is not None})  # Exclude None values
        return urljoin(base_url, path) + '?' + query_string

    def retrieve(self):
        exit_count = 3
        current_page = self.civitai_url
        while exit_count > 0:
            data = get_request_as_json(current_page)
            if isinstance(data, dict):
                item_list = []
                for item in data['items']:
                    if item['nsfwLevel'] == self.nsfw_level:
                        item_list.append(item)
                if len(item_list) >= self.limit:
                    print('Iam out')
                    media = self.convert_to_media(item_list[:self.limit])
                    return media
                exit_count -= 1
                if data.get('metadata') and data.get('metadata').get('nextPage'):
                    current_page = data['metadata']['nextPage']
                else:
                    break
            else:
                # Fehlerbehandlung
                print(f"Es gab einen Fehler bei der Anfrage: {data}")
                return None

    def convert_to_media(self, data):
        result = []
        if data:
            print(data)
            for item in data:
                media = Media(
                    creator=self.creator,
                    media_url=item['url'],
                    media_type=self.media_type,
                    likes=item['stats']['likeCount'],
                    hearts=item['stats']['heartCount'],
                    prompt=item['meta'].get('prompt') if item.get('meta') is not None else None,
                    model=item['meta'].get('Model').split('.')[0] if item.get('meta') is not None and
                                                                     item['meta'].get('Model') is not None else None,
                    author=item['username'],
                    tags=self.tags,
                    source_name='Civitai',
                    source_url=self.civitai_url,
                    media_created_at=item['createdAt']
                )
                result.append(media)
        return result


def main():
    load_dotenv()

    civitai_image_loader = CivitaiCollector(creator='CivitAIDailyTopImage', media_type='image', period='Day',
                                            nsfw=None, limit=3)
    data = civitai_image_loader.run()
    if data:
        print(data)
    civitai_hot_image_loader = CivitaiCollector(creator='CivitAIDailyTopHotImage', media_type='image',
                                                period='Day', nsfw='Mature', limit=3)
    data = civitai_hot_image_loader.run()
    if data:
        print(data)


if __name__ == "__main__":
    main()
