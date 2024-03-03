from unittest.mock import MagicMock

import pytest
import telebot

from main import create_url_extractor
from url import NoUrlException

@pytest.fixture
def extractor():
    return create_url_extractor()

def test_extract_url_from_text(extractor):
    mock_message = MagicMock(spec=telebot.types.Message)
    mock_message.text = 'Check out this link: https://www.example.com'
    mock_message.forward_from_message_id = None

    url = extractor.extract_url(mock_message)

    assert url == 'https://www.example.com'

def test_extract_url_from_forward(extractor):
    mock_message = MagicMock(spec=telebot.types.Message)
    mock_message.text = 'Hello world with link https://asdf.ru'
    mock_message.forward_from_chat.username = 'testchat'
    mock_message.forward_from_message_id = 123

    url = extractor.extract_url(mock_message)

    assert url == 'https://t.me/testchat/123?embed=1&mode=tme'

def test_no_url(extractor):
    mock_message = MagicMock(spec=telebot.types.Message)
    mock_message.text = 'Hello world'
    mock_message.forward_from_message_id = None

    with pytest.raises(NoUrlException):
        extractor.extract_url(mock_message)
