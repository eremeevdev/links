import pytest
from unittest.mock import MagicMock
import trafilatura

from analysis import TextInfo, UrlInfo
from analysis import DefaultUrlInfoFetcher, TgUrlInfoFetcher


class TestDefaultUrlInfoFetcher:

    @pytest.fixture
    def fetcher(self):
        analyzer = MagicMock()
        return DefaultUrlInfoFetcher(analyzer)

    @pytest.fixture
    def mock_fetch(self, monkeypatch):
        mock = MagicMock()
        monkeypatch.setattr(trafilatura, "fetch_url", mock)
        return mock

    @pytest.fixture
    def mock_metadata(self, monkeypatch):
        mock = MagicMock()
        monkeypatch.setattr(trafilatura, "extract_metadata", mock)
        return mock

    def test_success(self, fetcher, mock_fetch, mock_metadata):
        mock_fetch.return_value = "content"
        mock_metadata.return_value = MagicMock(title="title")

        analyzer = fetcher._analyzer
        analyzer.get_info.return_value = TextInfo(title="title", tags=["tag1", "tag2"], summary="summary")

        url_info = fetcher.get_info("http://example.com")

        assert url_info == UrlInfo(url="http://example.com", title="title", tags=["tag1", "tag2"], summary="summary")

    def test_fetch_failure(self, fetcher, mock_fetch, mock_metadata):
        mock_fetch.side_effect = Exception("Fetch error")

        url_info = fetcher.get_info("http://example.com")

        assert url_info == UrlInfo(url="http://example.com", title="N/A", tags=[], summary="")

    def test_analysis_failure(self, fetcher, mock_fetch, mock_metadata):
        mock_fetch.return_value = "content"
        mock_metadata.return_value = MagicMock(title="example.com")

        analyzer = fetcher._analyzer
        analyzer.get_info.side_effect = Exception("Analysis error")

        url_info = fetcher.get_info("http://example.com")

        assert url_info == UrlInfo(url="http://example.com", title="example.com", tags=[], summary="")


class TestTgUrlInfoFetcher:

    @pytest.fixture
    def fetcher(self):
        mock_analyzer = MagicMock()
        return TgUrlInfoFetcher(mock_analyzer)

    def test_return_none_for_non_tg_url(self, fetcher):
        assert fetcher.get_info("http://example.com") is None

    def test_return_urlinfo_for_tg_url(self, fetcher):
        url = "https://t.me/somechat/123"
        mock_text_info = TextInfo(title="Mock Title", tags=['tag'], summary="summary")
        fetcher._analyzer.get_info.return_value = mock_text_info

        info = fetcher.get_info(url)

        assert info == UrlInfo(
            url=url,
            title=mock_text_info.title,
            tags=mock_text_info.tags,
            summary=mock_text_info.summary
        )
