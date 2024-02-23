import telebot

from core import UrlHandler
import re


class NoUrlException(Exception):
	pass


def get_urls_from_text(message: telebot.types.Message) -> str:
	url_pattern = r'(https?://[^\s]+)'
	url_match = re.search(url_pattern, message.text)
	if url_match:
		return url_match.group(0)


def get_url_from_forward(message: telebot.types.Message):
	if message.forward_from_message_id is None:
		return

	return f'https://t.me/{message.forward_from_chat.username}/{message.forward_from_message_id}'


def extract_url(message: telebot.types.Message) -> str:
	for handler in [get_url_from_forward, get_urls_from_text]:
		url = handler(message)
		if url:
			return url

	raise NoUrlException(message.text)


class Bot:
	def __init__(self, token, handler: UrlHandler):
		self._bot = telebot.TeleBot(token)
		self._handler = handler

		self._bot.register_message_handler(self.send_welcome, commands=['start', 'help'])
		self._bot.register_message_handler(self.handle_url, func=lambda message: True)

	def send_welcome(self, message):
		self._bot.reply_to(message, "Howdy, how are you doing?")

	def handle_url(self, message: telebot.types.Message):
		self._bot.reply_to(message, 'wait...')
		url = extract_url(message)
		self._handler.handle(url)
		self._bot.reply_to(message, 'done')

	def run(self):
		self._bot.infinity_polling()
