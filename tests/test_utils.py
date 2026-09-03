import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd

from src.utils import get_user_settings, read_xlsx


@patch('src.utils.pd.read_excel')
def test_read_xlsx(mock_read_excel: Mock, utils_read_xlsx_data: pd.DataFrame) -> None:
    mock_read_excel.return_value = utils_read_xlsx_data
    pd.testing.assert_frame_equal(read_xlsx("test.xlsx"), utils_read_xlsx_data)
    mock_read_excel.assert_called_once_with("test.xlsx")


@patch('src.utils.pd.read_excel')
def test_read_xlsx_exception(mock_read_excel: Mock) -> None:
    mock_read_excel.side_effect = Exception
    pd.testing.assert_frame_equal(read_xlsx("test.xlsx"), pd.DataFrame())
    mock_read_excel.assert_called_once_with("test.xlsx")


def test_get_user_settings(utils_get_user_settings_data: str) -> None:
    with patch("builtins.open", mock_open(read_data=utils_get_user_settings_data)) as mock_builtins_open:
        result = get_user_settings()
        assert result == json.loads(utils_get_user_settings_data)
        mock_builtins_open.assert_called_once()


def test_get_user_settings_not_dict() -> None:
    with patch("builtins.open", mock_open(read_data="[\"USD\", \"EUR\"]")) as mock_builtins_open:
        result = get_user_settings()
        assert result == {}
        mock_builtins_open.assert_called_once()


def test_get_user_settings_exception() -> None:
    with patch("builtins.open", mock_open(read_data="")) as mock_builtins_open:
        mock_builtins_open.side_effect = Exception
        result = get_user_settings()
        assert result == {}
        mock_builtins_open.assert_called_once()
