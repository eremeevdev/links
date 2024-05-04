import json
import requests

from .core import TextInfo

prompt = """
Анализируя данный текст, нужно сформулировать:
- подходящий заголовок
- выбрать три ключевых тега
- написать краткое содержание состоящее из 2-3 предложений
- составить список ключевых слов

Заголовок должен отражать основную идею текста, теги — быть ясными и краткими, а краткое содержание — на русском языке и передавать суть текста в нескольких предложениях. 

Представьте результаты в JSON-формате. Шаблон для ответа:

{
  "title": "Здесь ваш заголовок",
  "tags": ["Тег1", "Тег2", "Тег3"],
  "keywords": ["ключевое слово1", "ключевое слово2", "ключевое слово3"],
  "summary": "Здесь ваше краткое содержание на русском языке"
}

текст:
```
%s
```
"""


class YandexGptTextAnalyzer:
    def __init__(self, api_key: str, catalog_id: str):
        self._api_key = api_key
        self._catalog_id = catalog_id
    
    def get_info(self, text: str) -> TextInfo:

        messages=[
            {"role": "user", "text": prompt % text},
        ]
        
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", json={
            "modelUri": f"gpt://{self._catalog_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "1000"
            },
            "messages": messages
        }, headers={"Authorization": f"Api-Key {self._api_key}"})
        
        text = response.json()['result']['alternatives'][0]['message']['text']

        data = json.loads(text)

        return TextInfo(**data)
