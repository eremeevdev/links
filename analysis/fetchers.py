import traceback

import trafilatura
from trafilatura.metadata import Document
from googleapiclient.discovery import build
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


class YTUrlInfoFetcher:
    '''
    Получение API ключа

    - Войдите в Google Cloud Console и создайте новый проект (или выберите существующий).
    - В поисковой строке наберите «YouTube Data API v3» и выберите соответствующий результат.
    - Нажмите «Enable» для активации API на вашем проекте.
    - В меню слева выберите «Credentials», затем «Create credentials» и «API key». Скопируйте полученный ключ.
    '''
    def __init__(self, api_key: str, analyzer: TextAnalyzer):
        self._analyzer = analyzer
        self._client = build("youtube", "v3", developerKey=api_key)

    def get_info(self, url: str) -> UrlInfo | None:
        if not url.startswith("https://www.youtube.com"):
            return None
        return self._get_info(url)

    def _extract_video_id(self, url: str) -> str:
        return url.split("=")[-1]

    def _get_video_info(self, url: str) -> UrlInfo:
        video_id = self._extract_video_id(url)
        video_response = self._client.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()

        return UrlInfo(
            url=url,
            title=video_response["items"][0]["snippet"]["title"],
            summary=video_response["items"][0]["snippet"]["description"],
            tags=[],
        )

    def _get_info(self, url: str) -> UrlInfo:
        url_info = self._get_video_info(url)
        text = f"{url_info.title}\n{url_info.summary}"
        text_info = self._analyzer.get_info(text)
        url_info.tags = text_info.tags
        return url_info
