import os
import logging
from dataclasses import dataclass

import dotenv

from analysis import DefaultUrlInfoFetcher
from analysis import GptTextAnalyzer, YandexGptTextAnalyzer
from analysis import NotionUrlInfoStore
from analysis import UrlHandler, UrlInfoFetcherContext, TgUrlInfoFetcher, YTUrlInfoFetcher
from bot import Bot
from bot import create_url_extractor


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Config:
    notion_database_id: str
    notion_api_key: str
    gpt_api_key: str
    tg_api_key: str
    yt_api_key: str
    yandex_gpt_key: str
    yandex_gpt_catalog: str

    @staticmethod
    def from_env() -> "Config":
        return Config(
            notion_database_id=os.environ.get("NOTION_DATABASE_ID"),
            notion_api_key=os.environ.get("NOTION_API_KEY"),
            gpt_api_key=os.environ.get("GPT_API_KEY"),
            tg_api_key=os.environ.get("TG_API_KEY"),
            yt_api_key=os.environ.get("YT_API_KEY"),
            yandex_gpt_key=os.environ.get("YANDEX_GPT_KEY"),
            yandex_gpt_catalog=os.environ.get("YANDEX_GPT_CATALOG")
        )


def create_info_fetcher(config: Config) -> UrlInfoFetcherContext:
    text_analyzer = YandexGptTextAnalyzer(config.yandex_gpt_key, config.yandex_gpt_catalog)

    strategies = [
        YTUrlInfoFetcher(config.yt_api_key, text_analyzer),
        TgUrlInfoFetcher(text_analyzer),
        DefaultUrlInfoFetcher(text_analyzer),
    ]

    return UrlInfoFetcherContext(strategies)


def create_url_handler(config: Config) -> UrlHandler:

    url_info_fetcher = create_info_fetcher(config)
    store = NotionUrlInfoStore(config.notion_api_key, config.notion_database_id)

    handler = UrlHandler(url_info_fetcher, store)

    return handler


def main():
    dotenv.load_dotenv()

    config = Config.from_env()

    handler = create_url_handler(config)
    url_extractor = create_url_extractor()

    bot = Bot(config.tg_api_key, handler, url_extractor)

    logger.error("start")
    bot.run()


if __name__ == "__main__":
    main()
