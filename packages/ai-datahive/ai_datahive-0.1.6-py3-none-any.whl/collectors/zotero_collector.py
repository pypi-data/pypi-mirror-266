import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from ai_datahive.models import Media
from ai_datahive.collectors import BaseCollector
from ai_datahive.collectors import ZoteroHelper


class ZoteroCollector(BaseCollector):

    def __init__(self, collection_name, content_type='media', creator_name='ZoteroCollector', zotero_api_key=None,
                 zotero_library_id=None, zotero_library_type='user', all_types=False, tags=None, limit=3):

        zotero_api_key = os.getenv('ZOTERO_API_KEY') if zotero_api_key is None else zotero_api_key
        zotero_library_id = os.getenv('ZOTERO_USER_ID') if zotero_library_id is None else zotero_library_id

        self.zotero_library_id = zotero_library_id
        self.collection_name = collection_name
        self.limit = limit
        self.all_types = all_types
        self.content_type = content_type
        self.zotero_helper = ZoteroHelper(zotero_api_key, zotero_library_id, zotero_library_type)

        super().__init__(creator_name=creator_name, content_type=content_type)

    def build_tags(self, itemType, repository):
        tags = 'zotero, '
        if itemType:
            tags += itemType + ', '
        if repository:
            tags += repository + ', '

        tags = tags.rstrip(', ')
        return tags

    def retrieve(self):
        if self.collection_name is None or self.limit is None:
            raise ValueError('collection_name and limit must be defined')

        # Get date from the latest message to the telegram table - using topic / reporter
        latest_message_date = self.get_latest_message_date()
        print(latest_message_date)
        if latest_message_date is None:
            latest_message_date = (datetime.now() - timedelta(days=7))

        # Get everything what is new in the defined collection after that date
        entries = (self.zotero_helper
                   .get_latest_created_after_by_collection_name(latest_message_date, self.collection_name,
                                                                limit=self.limit, all_types=self.all_types))
        return entries

    # TODO needs to be changed after a good way of using a multi media collector is found
    def convert_to_media(self, data):
        if data:
            if self.content_type == 'media':
                creators = data['data'].get('creators', [])
                full_names = [f"{creator['firstName']} {creator['lastName']}" for creator in creators]

                # Format output
                if len(full_names) > 3:
                    output_creators = ', '.join(full_names[:3]) + ', et al.'
                else:
                    output_creators = ', '.join(full_names)

                media = Media(
                    creator=self.creator_name,
                    media_type='paper',
                    title=data['data'].get('title', ''),
                    description=data['data'].get('abstractNote', ''),
                    author=output_creators,
                    tags=self.build_tags(data['data'].get('itemType'), data['data'].get('repository')),
                    source='Zotero - ' + self.zotero_library_id,
                    media_created_at=data['data'].get('date', ''),
                    reference_url=data['data'].get('url')
                )
                return media


def main():
    load_dotenv()
    zotero_collector = ZoteroCollector(collection_name='Papers/arxiv')
    data = zotero_collector.retrieve()
    #print(data)
    #trans = zotero_collector.convert_to_media(data[0])
    #print(trans)
    result = zotero_collector.save(data)
    print(result)


if __name__ == "__main__":
    main()
