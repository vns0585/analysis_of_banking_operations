from os import remove

import pandas as pd
import pytest
from unittest.mock import patch, Mock

from src.reports import report, spending_by_weekday


def test_report() -> None:
    @report()
    def my_function(x: int,
                    y: int) -> int:
        return x + y
    result = my_function(1, 2)
    with open("report.txt", "r", encoding="utf-8") as file:
        assert file.read() == str(result)
    remove("report.txt")


def test_report_file_name() -> None:
    @report("my_function.txt")
    def my_function(x: str,
                    y: str) -> str:
        return x + y
    result = my_function("Привет, ", "мир!")
    with open("my_function.txt", "r", encoding="utf-8") as file:
        assert file.read() == str(result)
    remove("my_function.txt")


def test_report_func_exception() -> None:
    @report()
    def my_function() -> str:
        raise Exception
    with pytest.raises(Exception):
        my_function()


def test_report_file_not_wrote() -> None:
    with patch("builtins.open", side_effect=PermissionError) as mock_open:
        @report("my_function.txt")
        def my_function(x: str,
                        y: str) -> str:
            return x + y
        my_function("Привет, ", "мир!")
        mock_open.assert_called_once()


def test_spending_by_weekday(reports_transactions: pd.DataFrame, reports_result: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(spending_by_weekday(reports_transactions), reports_result)


def test_spending_by_weekday_empty_df() -> None:
    pd.testing.assert_frame_equal(spending_by_weekday(pd.DataFrame()), pd.DataFrame())


def test_spending_by_weekday_date(reports_transactions: pd.DataFrame, reports_result: pd.DataFrame) -> None:
    result = reports_result[reports_result["День недели"] != "Sunday"]
    pd.testing.assert_frame_equal(spending_by_weekday(reports_transactions, "2026.08.30 00:00:00"), result)


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame({"Дата операции": ["29.01.2026", "30.08.2026"]}),
        pd.DataFrame({"Сумма платежа": [100, 500]}),
    ]
)
def test_spending_by_weekday_without_column(df: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(spending_by_weekday(df), pd.DataFrame())
