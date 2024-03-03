import re
from typing import Protocol, Optional, List

import telebot


class NoUrlException(Exception):
    pass


class UrlExtractor(Protocol):
    def extract(self, message: telebot.types.Message) -> Optional[str]:
        ...


class UrlFromTextExtractor:
    def extract(self, message: telebot.types.Message) -> Optional[str]:
        url_pattern = r'(https?://[^\s]+)'
        url_match = re.search(url_pattern, message.text)
        if url_match:
            return url_match.group(0)


class UrlFromForwardExtractor:
    def extract(self, message: telebot.types.Message) -> Optional[str]:
        if message.forward_from_message_id is None:
            return
        return f'https://t.me/{message.forward_from_chat.username}/{message.forward_from_message_id}?embed=1&mode=tme'


class UrlExtractorContext:
    def __init__(self, strategies: List[UrlExtractor]) -> None:
        self._strategies = strategies

    def extract_url(self, message: telebot.types.Message) -> str:
        for strategy in self._strategies:
            url = strategy.extract(message)
            if url:
                return url

        raise NoUrlException(message.text)


def create_url_extractor() -> UrlExtractorContext:
    strategies = [UrlFromForwardExtractor(), UrlFromTextExtractor()]
    return UrlExtractorContext(strategies)
