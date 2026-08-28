from unittest.mock import patch, Mock
import pytest
import pandas as pd
from src.services import find_phone_numbers
from tests.conftest import services_find_phone_numbers


@patch('src.services.read_xlsx')
def test_find_phone_numbers(mock_read_xlsx: Mock, utils_read_xlsx_data: pd.DataFrame, services_find_phone_numbers: str) -> None:
    mock_read_xlsx.return_value = utils_read_xlsx_data
    print(find_phone_numbers())
    assert find_phone_numbers() == services_find_phone_numbers
    mock_read_xlsx.assert_called_once()

@pytest.mark.parametrize("phone_numbers, expected",
                         [
                             ( [{"Описание": "Колхоз 89200000000"}],"[{\"Описание\": \"Колхоз 89200000000\"}]"),
                         ]
                         )
def test_find_phone_numbers_no_numbers(phone_numbers: list[dict], expected: str) -> None:
    with patch('src.services.read_xlsx') as mock_read_xlsx:
        mock_read_xlsx.return_value = pd.DataFrame(phone_numbers)
        assert find_phone_numbers() == expected
        mock_read_xlsx.assert_called_once()
