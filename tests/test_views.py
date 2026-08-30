from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import get_cards, get_currency_rates, get_greeting, get_top_transactions


@pytest.mark.parametrize("hour, expected", [
    *[(h, "Доброй ночи") for h in range(0, 6)],
    *[(h, "Доброе утро") for h in range(6, 12)],
    *[(h, "Добрый день") for h in range(12, 18)],
    *[(h, "Добрый вечер") for h in range(18, 24)],
])
@patch('src.views.datetime')
def test_get_greeting(mock_datetime: Mock, hour: int, expected: str) -> None:
    mock_datetime.now.return_value = datetime(2020, 1, 1, hour, 0, 0, 0)
    assert get_greeting() == expected
    mock_datetime.now.assert_called_once()


def test_get_cards(views_df: pd.DataFrame, views_get_cards_list: list) -> None:
    assert get_cards(views_df) == views_get_cards_list


def test_get_cards_empty_df() -> None:
    assert get_cards(pd.DataFrame()) == []


def test_get_cards_empty_values_df() -> None:
    df = pd.DataFrame(columns=["Номер карты", "Сумма платежа", "Кэшбэк"])
    assert get_cards(df) == []


def test_get_top_transactions(views_df: pd.DataFrame, views_get_top_transactions_list: list) -> None:
    assert get_top_transactions(views_df) == views_get_top_transactions_list


def test_get_top_transactions_empty_df() -> None:
    assert get_top_transactions(pd.DataFrame()) == []


def test_get_top_transactions_empty_values_df() -> None:
    df = pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Категория", "Описание"])
    assert get_top_transactions(df) == []


@patch("src.views.get_user_settings")
@patch("src.views.requests.get")
@patch("src.views.os.getenv")
def test_get_currency_rates(mock_os_getenv: Mock,
                            mock_get: Mock,
                            mock_settings: Mock,
                            views_user_settings: dict,
                            views_currency_response: dict,
                            views_currency_result: list[dict]) -> None:

    mock_settings.return_value = views_user_settings
    mock_os_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = views_currency_response
    mock_get.return_value = mock_response

    result = get_currency_rates()

    assert len(result) == 3
    assert result == views_currency_result

    expected_params = {
        "get": "rates",
        "pairs": "USDRUB,EURRUB,GBPRUB",
        "key": "test_api_key"
    }
    mock_get.assert_called_once_with(
        "https://currate.ru/api/",
        params=expected_params
    )


@patch("src.views.get_user_settings")
def test_get_currency_rates_empty_settings(mock_settings: Mock) -> None:
    mock_settings.return_value = {}
    assert get_currency_rates() == []
    mock_settings.assert_called_once()


@patch("src.views.get_user_settings")
@patch("src.views.requests.get")
@patch("src.views.os.getenv")
def test_get_currency_rates_wrong_response(mock_os_getenv: Mock,
                                           mock_get: Mock,
                                           mock_settings: Mock,
                                           views_user_settings: dict) -> None:

    mock_settings.return_value = views_user_settings
    mock_os_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    result = get_currency_rates()

    assert result == []

    expected_params = {
        "get": "rates",
        "pairs": "USDRUB,EURRUB,GBPRUB",
        "key": "test_api_key"
    }
    mock_get.assert_called_once_with(
        "https://currate.ru/api/",
        params=expected_params
    )
