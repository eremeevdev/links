from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from notion import NotionUrlInfoStore
from core import UrlInfo


class TestNotionUrlInfoStore:

    @pytest.fixture
    def store(self, mocker: MockerFixture):
        mocker.patch("notion.NotionClient")
        return NotionUrlInfoStore("key", "db_id")

    def test_create_page(self, store):

        info = UrlInfo("Example", "https://example.com", ["tag1", "tag2"], "summary")

        store.create_page(info)

        store._client.pages.create.assert_called_once_with(
            parent={"type": "database_id", "database_id": "db_id"},
            properties={
                "Name": {"title": [{"text": {"content": info.title}}]},
                "URL": {"url": info.url},
                "Tags": {"multi_select": [{"name": tag} for tag in info.tags]},
                "List": {"select": {"name": "Inbox"}},
            },
            children=[{"object": "block", "paragraph": {"rich_text": [{"text": {"content": info.summary}}]}}],
        )
