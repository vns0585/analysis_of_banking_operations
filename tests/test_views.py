import json
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import get_cards, get_currency_rates, get_greeting, get_stock_prices, get_top_transactions, process_data


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


def test_get_top_transactions_wrong_dates() -> None:
    df = pd.DataFrame(
        {
            "Дата операции": [None, None],
            "Сумма платежа": [100, 200],
            "Категория": ["1", "2"],
            "Описание": ["1", "2"]
        }
    )
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


@patch("src.views.get_user_settings")
@patch("src.views.requests.get")
@patch("src.views.os.getenv")
def test_get_stock_prices(mock_os_getenv: Mock,
                          mock_get: Mock,
                          mock_settings: Mock,
                          views_user_settings: dict,
                          views_stock_response: dict,
                          views_stock_result: list[dict]) -> None:

    mock_settings.return_value = views_user_settings
    mock_os_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = views_stock_response
    mock_get.return_value = mock_response

    result = get_stock_prices()

    assert len(result) == 1
    assert result == views_stock_result

    expected_headers = {"X-Api-Key": "test_api_key"}
    expected_params = {"ticker": "AAPL"}
    mock_get.assert_called_once_with(
        "https://api.api-ninjas.com/v1/stockprice",
        params=expected_params,
        headers=expected_headers
    )


@patch("src.views.get_user_settings")
def test_get_stock_prices_empty_user_settings(mock_settings: Mock) -> None:
    mock_settings.return_value = {}
    assert get_stock_prices() == []


@patch("src.views.get_user_settings")
@patch("src.views.requests.get")
@patch("src.views.os.getenv")
def test_get_stock_prices_wrong_response(mock_os_getenv: Mock,
                                         mock_get: Mock,
                                         mock_settings: Mock,
                                         views_user_settings: dict) -> None:

    mock_settings.return_value = views_user_settings
    mock_os_getenv.return_value = "test_api_key"

    mock_response = Mock()
    mock_response.status_code = 504
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    result = get_stock_prices()

    assert result == [{}]

    expected_headers = {"X-Api-Key": "test_api_key"}
    expected_params = {"ticker": "AAPL"}
    mock_get.assert_called_once_with(
        "https://api.api-ninjas.com/v1/stockprice",
        params=expected_params,
        headers=expected_headers
    )


@patch("src.views.get_user_settings")
@patch("src.views.requests.get")
@patch("src.views.os.getenv")
def test_get_stock_prices_api_key_none(mock_os_getenv: Mock,
                                       mock_get: Mock,
                                       mock_settings: Mock,
                                       views_user_settings: dict,
                                       views_stock_response: dict,
                                       views_stock_result: list[dict]) -> None:

    mock_settings.return_value = views_user_settings
    mock_os_getenv.return_value = None

    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = "{'error': 'Missing API Key.'}"
    mock_get.return_value = mock_response

    result = get_stock_prices()

    assert len(result) == 1
    assert result == [{}]

    expected_headers: dict = {}
    expected_params = {"ticker": "AAPL"}
    mock_get.assert_called_once_with(
        "https://api.api-ninjas.com/v1/stockprice",
        params=expected_params,
        headers=expected_headers
    )


@patch("src.views.get_greeting")
@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch('src.views.read_xlsx')
def test_process_data(mock_read_xlsx: Mock,
                      mock_get_currency_rates: Mock,
                      mock_get_stock_prices: Mock,
                      mock_get_greeting: Mock,
                      utils_read_xlsx_data: pd.DataFrame,
                      views_currency_result: list,
                      views_stock_result: list,
                      process_data_result: dict) -> None:
    mock_read_xlsx.return_value = utils_read_xlsx_data
    mock_get_currency_rates.return_value = views_currency_result
    mock_get_stock_prices.return_value = views_stock_result
    mock_get_greeting.return_value = "Доброе утро"
    assert process_data("2021-12-31 23:59:59") == process_data_result
    mock_read_xlsx.assert_called_once()
    mock_get_currency_rates.assert_called_once()
    mock_get_stock_prices.assert_called_once()
    mock_get_greeting.assert_called_once()


@patch('src.views.read_xlsx')
def test_process_data_empty_xlsx(mock_read_xlsx: Mock, utils_read_xlsx_data: pd.DataFrame) -> None:
    df = utils_read_xlsx_data.drop("Дата операции", axis=1)
    mock_read_xlsx.return_value = df
    assert process_data("2021-12-31 23:59:59") == json.dumps({})
    mock_read_xlsx.assert_called_once()


@patch('src.views.read_xlsx')
def test_process_data_without_column(mock_read_xlsx: Mock, ) -> None:
    mock_read_xlsx.return_value = pd.DataFrame()
    assert process_data("2021-12-31 23:59:59") == json.dumps({})
    mock_read_xlsx.assert_called_once()
