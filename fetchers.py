import trafilatura

from core import TextAnalyzer, UrlInfo


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
            tags=text_info.tags,
            summary=text_info.summary
        )

        return url_info
