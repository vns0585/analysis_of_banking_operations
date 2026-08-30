import json
from unittest.mock import Mock, patch

import pandas as pd

from src.services import find_phone_numbers


@patch("src.services.read_xlsx")
def test_find_phone_numbers(mock_read_xlsx: Mock) -> None:
    test_data = {
        "Описание": [
            "Оператор +7 999 123-45-67",
            "Оператор 8 (999) 123-45-67",
            "Тел: +7-999-123-45-67",
            "8-999-123-45-67",
            "Нет номера",
            "Сообщение",
            "Неверный номер 8 910 00-00-00"
        ],
        "Сумма": [1, 2, 3, 4, 5, 6, 7]
    }
    mock_df = pd.DataFrame(test_data)
    mock_read_xlsx.return_value = mock_df
    result = find_phone_numbers()
    result_data = json.loads(result)
    assert len(result_data) == 4
    for i in range(len(result_data)):
        assert result_data[i]["Описание"] == test_data["Описание"][i]  # type: ignore[index]


@patch("src.services.read_xlsx")
def test_find_phone_numbers_void_dataframe(mock_read_xlsx: Mock) -> None:
    mock_df = pd.DataFrame()
    mock_read_xlsx.return_value = mock_df
    result = find_phone_numbers()
    assert result == json.dumps([])


@patch("src.services.read_xlsx")
def test_find_phone_numbers_without_column(mock_read_xlsx: Mock) -> None:
    test_data = {
        "Правописание": [
            "Оператор +7 999 123-45-67",
            "Оператор 8 (999) 123-45-67",
            "Тел: +7-999-123-45-67",
            "8-999-123-45-67",
            "Нет номера",
            "Сообщение",
            "Неверный номер 8 910 00-00-00"
        ],
        "Сумма": [1, 2, 3, 4, 5, 6, 7]
    }
    mock_df = pd.DataFrame(test_data)
    mock_read_xlsx.return_value = mock_df
    result = find_phone_numbers()
    assert result == json.dumps([])
