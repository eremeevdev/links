import telebot

from core import UrlHandler


class Bot:
	def __init__(self, token, handler: UrlHandler):
		self._bot = telebot.TeleBot(token)
		self._handler = handler

		self._bot.register_message_handler(self.send_welcome, commands=['start', 'help'])
		self._bot.register_message_handler(self.handle_url, func=lambda message: True)

	def send_welcome(self, message):
		self._bot.reply_to(message, "Howdy, how are you doing?")

	def handle_url(self, message):
		self._bot.reply_to(message, 'wait...')
		self._handler.handle(message.text)
		self._bot.reply_to(message, 'done')

	def run(self):
		self._bot.infinity_polling()
