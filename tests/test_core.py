from unittest.mock import MagicMock

import pytest

from analysis import UrlHandler, UrlInfo, UrlInfoStore
from analysis import UrlInfoFetcherContext, UrlInfoFetcher, NoUrlInfoFetcherException


class TestUrlHandler:

    @pytest.fixture
    def fetcher(self):
        return MagicMock(UrlInfoFetcherContext)

    @pytest.fixture
    def store(self):
        return MagicMock(UrlInfoStore)

    def test_handle(self, fetcher, store):
        fetcher.get_info.return_value = UrlInfo("Title", "http://url.com", ["tag1"], "summary", ["k"])

        handler = UrlHandler(fetcher, store)

        url = "http://url.com"
        handler.handle(url)

        fetcher.get_info.assert_called_with(url)
        store.create_page.assert_called_with(UrlInfo("Title", "http://url.com", ["tag1"], "summary", ["k"]))

    def test_handle_exception(self, fetcher, store):
        fetcher.get_info.side_effect = Exception("Error")

        handler = UrlHandler(fetcher, store)

        url = "http://url.com"
        handler.handle(url)

        store.create_page.assert_called_with(UrlInfo("N/A", "http://url.com", [], "", []))


class TestUrlInfoFetcherContext:

    @pytest.fixture
    def mock_fetcher(self) -> MagicMock:
        return MagicMock(spec=UrlInfoFetcher)

    def test_returns_info_from_first_matching_strategy(self):
        url = "http://example.com"
        expected = UrlInfo("title", url, ["tag"], "summary", ["k"])

        strategies = [
            MagicMock(get_info=MagicMock(return_value=None)),
            MagicMock(get_info=MagicMock(return_value=None)),
            MagicMock(get_info=MagicMock(return_value=expected)),
        ]
        context = UrlInfoFetcherContext(strategies)

        actual = context.get_info(url)
        assert actual == expected

    def test_raises_if_no_match(self, mock_fetcher):
        url = "http://example.com"

        mock_fetcher.get_info.return_value = None

        strategies = [mock_fetcher]
        context = UrlInfoFetcherContext(strategies)

        with pytest.raises(NoUrlInfoFetcherException):
            context.get_info(url)
