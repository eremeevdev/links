import os
from dataclasses import dataclass

import dotenv
from bot import Bot
from core import UrlHandler, GptTextAnalyzer, DefaultUrlInfoFetcher, UrlInfoFetcherChain, NotionUrlInfoStore


@dataclass
class Config:
    notion_database_id: str
    notion_api_key: str
    gpt_api_key: str
    tg_api_key: str

    @staticmethod
    def from_env() -> 'Config':
        return Config(
            notion_database_id=os.environ.get('NOTION_DATABASE_ID'),
            notion_api_key=os.environ.get('NOTION_API_KEY'),
            gpt_api_key=os.environ.get('GPT_API_KEY'),
            tg_api_key=os.environ.get('TG_API_KEY')
        )


def create_default_handler(config: Config) -> UrlHandler:
    analyzer = GptTextAnalyzer(config.gpt_api_key)
    default_fetcher = DefaultUrlInfoFetcher(analyzer)

    chain = UrlInfoFetcherChain()
    chain.register_fetcher(default_fetcher)

    store = NotionUrlInfoStore(config.notion_api_key, config.notion_database_id)

    handler = UrlHandler(chain, store)

    return handler


def main():
    dotenv.load_dotenv()

    config = Config.from_env()
    handler = create_default_handler(config)
    bot = Bot(config.tg_api_key, handler)
    bot.run()


if __name__ == '__main__':
    main()
