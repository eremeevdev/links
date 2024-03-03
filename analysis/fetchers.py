import traceback

import trafilatura

from .core import TextAnalyzer, UrlInfo, TextInfo


class DefaultUrlInfoFetcher:
    def __init__(self, analyzer: TextAnalyzer):
        self._analyzer = analyzer

    def get_info(self, url: str) -> UrlInfo | None:
        try:
            downloaded = trafilatura.fetch_url(url)
        except Exception as e:
            traceback.print_exc()
            return UrlInfo(url=url, title="N/A", tags=[], summary="")

        meta: trafilatura.metadata.Document = trafilatura.extract_metadata(downloaded)
        text: str = trafilatura.extract(downloaded)

        try:
            text_info = self._analyzer.get_info(text)
        except:
            traceback.print_exc()
            text_info = TextInfo.empty()

        url_info = UrlInfo(url=url, title=meta.title, tags=text_info.tags, summary=text_info.summary)

        return url_info
