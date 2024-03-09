import traceback

import trafilatura
from trafilatura.metadata import Document

from .core import TextAnalyzer, UrlInfo, TextInfo


class DefaultUrlInfoFetcher:
    def __init__(self, analyzer: TextAnalyzer):
        self._analyzer = analyzer

    def _build_url_info(self, url: str, meta: Document, text_info: TextInfo) -> UrlInfo:
        return UrlInfo(url=url, title=meta.title, tags=text_info.tags, summary=text_info.summary)

    def get_info(self, url: str) -> UrlInfo | None:
        try:
            downloaded = trafilatura.fetch_url(url)
        except Exception as e:
            traceback.print_exc()
            return UrlInfo(url=url, title="N/A", tags=[], summary="")

        meta: Document = trafilatura.extract_metadata(downloaded)
        text: str = trafilatura.extract(downloaded)

        try:
            text_info = self._analyzer.get_info(text)
        except:
            traceback.print_exc()
            text_info = TextInfo.empty()

        return self._build_url_info(url, meta, text_info)


class TgUrlInfoFetcher(DefaultUrlInfoFetcher):
    def get_info(self, url: str) -> UrlInfo | None:
        if not url.startswith("https://t.me"):
            return None
        return super().get_info(url)

    def _build_url_info(self, url: str, meta: Document, text_info: TextInfo) -> UrlInfo:
        return UrlInfo(url=url, title=text_info.title, tags=text_info.tags, summary=text_info.summary)
