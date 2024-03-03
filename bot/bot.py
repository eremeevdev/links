import telebot

from analysis import UrlHandler
from .url import UrlExtractorContext


class Bot:
    def __init__(self, token, handler: UrlHandler, extractor: UrlExtractorContext):
        self._bot = telebot.TeleBot(token)
        self._handler = handler
        self._extractor = extractor

        self._bot.register_message_handler(self.send_welcome, commands=["start", "help"])
        self._bot.register_message_handler(self.handle_url, func=lambda message: True)

    def send_welcome(self, message):
        self._bot.reply_to(message, "Howdy, how are you doing?")

    def handle_url(self, message: telebot.types.Message):
        self._bot.reply_to(message, "wait...")
        url = self._extractor.extract_url(message)
        self._handler.handle(url)
        self._bot.reply_to(message, "done")

    def run(self):
        self._bot.infinity_polling()
