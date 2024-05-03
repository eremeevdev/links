from notion_client import Client as NotionClient
from .core import UrlInfo


class NotionUrlInfoStore:
    def __init__(self, auth: str, database_id: str):
        self._database_id = database_id
        self._client = NotionClient(auth=auth)

    def create_page(self, info: UrlInfo):
        params = {
            "parent": {"type": "database_id", "database_id": self._database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": info.title}}]},
                "URL": {"url": info.url},
                "Tags": {"multi_select": [{"name": tag} for tag in info.tags]},
                "List": {"select": {"name": "Inbox"}},
            },
            "children": [
                {"object": "block", "paragraph": {"rich_text": [{"text": {"content": info.summary}}]}},
                {"object": "block", "paragraph": {"rich_text": [{"text": {"content": ", ".join(info.keywords)}}]}},
            ],
        }

        self._client.pages.create(**params)
