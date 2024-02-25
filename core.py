import json
import traceback
from dataclasses import dataclass
from typing import List, Protocol

import trafilatura
from notion_client import Client as NotionClient
from openai import OpenAI


@dataclass
class UrlInfo:
    title: str
    url: str
    tags: List[str]


@dataclass
class TextInfo:
    title: str
    tags: List[str]


class UrlInfoFetcher(Protocol):
    def get_info(self, url: str) -> UrlInfo | None:
        ...


class TextAnalyzer(Protocol):
    def get_info(self, text: str) -> TextInfo:
        ...


class UrlInfoStore(Protocol):
    def create_page(self, info: UrlInfo):
        ...


class UrlInfoFetcherContext:
    def __init__(self):
        self._items: List[UrlInfoFetcher] = []

    def register_fetcher(self, item: UrlInfoFetcher) -> None:
        self._items.append(item)

    def get_info(self, url: str) -> UrlInfo | None:
        for item in self._items:
            inf = item.get_info(url)
            if inf is not None:
                return inf


class UrlHandler:
    def __init__(self, fetcher: UrlInfoFetcher, store: UrlInfoStore):
        self._fetcher = fetcher
        self._store = store

    def handle(self, url: str):
        try:
            info = self._fetcher.get_info(url)
        except Exception as e:
            traceback.print_exc()
            info = UrlInfo(title="N/A", url=url, tags=[])

        if info is not None:
            self._store.create_page(info)


class GptTextAnalyzer:
    def __init__(self, api_key):
        self._client = OpenAI(api_key=api_key)

    def get_info(self, text: str) -> TextInfo:
        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Дан текст, определи 3 главных тега и заголовок, которые могли бы описать этот текст. Теги должны быть короткими и понятными ключевыми словами или фразами. Результат должен быть в формате json."},
                {"role": "user", "content": "Architecture decision record (ADR) / Architecture decision log (ADL) — это регулярная фиксация принятых и непринятых в ходе разработки программного обеспечения решений, затрагивающих дизайн, проектирование, выбор инструментов и подходов, и отвечающих определенным функциональным или нефункциональным требованиям."},
                {"role": "assistant", "content": '{"tags": ["adr","architecture","software development"], "title":"Что такое ADR"}'},
                {"role": "user", "content": text}
            ]
        )

        data = json.loads(response.choices[0].message.content)

        return TextInfo(**data)


class DefaultUrlInfoFetcher:
    def __init__(self, analyzer: TextAnalyzer):
        self._analyzer = analyzer

    def get_info(self, url: str) -> UrlInfo | None:
        downloaded = trafilatura.fetch_url(url)

        meta: trafilatura.metadata.Document = trafilatura.extract_metadata(downloaded)
        text: str = trafilatura.extract(downloaded)

        text_info = self._analyzer.get_info(text)

        url_info = UrlInfo(
            url=url,
            title=meta.title,
            tags=text_info.tags
        )

        return url_info


class NotionUrlInfoStore:
    def __init__(self, auth: str, database_id: str):
        self._database_id = database_id
        self._client = NotionClient(auth=auth)

    def create_page(self, info: UrlInfo):
        params = {
            "parent": {
                "type": "database_id",
                "database_id": self._database_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": info.title
                            }
                        }
                    ]
                },
                "URL": {
                    "url": info.url
                },
                "Tags": {
                    "multi_select": [{"name": tag} for tag in info.tags]
                },
                "List": {
                    "select": {
                        "name": "Inbox"
                    }
                }
            },
        }

        self._client.pages.create(**params)
