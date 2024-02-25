import json

from openai import OpenAI

from core import TextInfo


class GptTextAnalyzer:
    def __init__(self, api_key):
        self._client = OpenAI(api_key=api_key)

    def get_info(self, text: str) -> TextInfo:
        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Дан текст, определи заголовок, 3 главных тега и summary, которые могли бы описать этот текст. Теги должны быть короткими и понятными ключевыми словами или фразами. Результат должен быть в формате json."},
                {"role": "user", "content": "Architecture decision record (ADR) / Architecture decision log (ADL) — это регулярная фиксация принятых и непринятых в ходе разработки программного обеспечения решений, затрагивающих дизайн, проектирование, выбор инструментов и подходов, и отвечающих определенным функциональным или нефункциональным требованиям."},
                {"role": "assistant", "content": '{"tags": ["adr","architecture","software development"], "title":"Что такое ADR", "summary": "В статье рассказывается что такое ADR и для чего это нгужно"}'},
                {"role": "user", "content": text}
            ]
        )

        data = json.loads(response.choices[0].message.content)

        return TextInfo(**data)
