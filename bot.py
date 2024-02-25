from typing import Protocol, Optional, List

import telebot

from core import UrlHandler
import re


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

		return f'https://t.me/{message.forward_from_chat.username}/{message.forward_from_message_id}'


class UrlExtractorContext:
	def __init__(self, strategies: List[UrlExtractor]) -> None:
		self._strategies = strategies

	def extract_url(self, message: telebot.types.Message) -> str:
		for strategy in self._strategies:
			url = strategy.extract(message)
			if url:
				return url

		raise NoUrlException(message.text)


class Bot:
	def __init__(self, token, handler: UrlHandler, extractor: UrlExtractorContext):
		self._bot = telebot.TeleBot(token)
		self._handler = handler
		self._extractor = extractor

		self._bot.register_message_handler(self.send_welcome, commands=['start', 'help'])
		self._bot.register_message_handler(self.handle_url, func=lambda message: True)

	def send_welcome(self, message):
		self._bot.reply_to(message, "Howdy, how are you doing?")

	def handle_url(self, message: telebot.types.Message):
		self._bot.reply_to(message, 'wait...')
		url = self._extractor.extract_url(message)
		self._handler.handle(url)
		self._bot.reply_to(message, 'done')

	def run(self):
		self._bot.infinity_polling()
