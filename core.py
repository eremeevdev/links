import traceback
from dataclasses import dataclass
from typing import List, Protocol

import trafilatura


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
    def __init__(self, strategies: List[UrlInfoFetcher]):
        self.strategies = strategies

    def get_info(self, url: str) -> UrlInfo | None:
        for item in self.strategies:
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
