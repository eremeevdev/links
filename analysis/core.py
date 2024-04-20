import traceback
from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class UrlInfo:
    title: str
    url: str
    tags: List[str]
    summary: str
    keywords: List[str]


@dataclass
class TextInfo:
    title: str
    tags: List[str]
    summary: str
    keywords: List[str]

    @staticmethod
    def empty() -> "TextInfo":
        return TextInfo(title="", tags=[], summary="")


class UrlInfoFetcher(Protocol):
    def get_info(self, url: str) -> UrlInfo | None: ...


class TextAnalyzer(Protocol):
    def get_info(self, text: str) -> TextInfo: ...


class UrlInfoStore(Protocol):
    def create_page(self, info: UrlInfo): ...


class NoUrlInfoFetcherException(Exception):
    pass


class UrlInfoFetcherContext:
    def __init__(self, strategies: List[UrlInfoFetcher]):
        self.strategies = strategies

    def get_info(self, url: str) -> UrlInfo:
        for item in self.strategies:
            inf = item.get_info(url)
            if inf is not None:
                return inf

        raise NoUrlInfoFetcherException(url)


class UrlHandler:
    def __init__(self, fetcher: UrlInfoFetcherContext, store: UrlInfoStore):
        self._fetcher = fetcher
        self._store = store

    def handle(self, url: str):
        try:
            info = self._fetcher.get_info(url)
        except Exception as e:
            traceback.print_exc()
            info = UrlInfo(title="N/A", url=url, tags=[], summary="")

        self._store.create_page(info)
