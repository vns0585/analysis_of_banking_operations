from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import read_xlsx


def report(path: str = "report.txt") -> Callable:
    """Декоратор записывающий результаты работы функции в файл"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            with open(path, "w") as file:
                file.write(result)
            return result
        return wrapper
    return decorator


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает DataFrame со средним значением трат в каждый из дней недели
    за последние три месяца (от переданной даты)."""
    if date is None:
        end_date = datetime.today()
    else:
        end_date = pd.to_datetime(date)
    start_date = pd.Timestamp(end_date) - pd.DateOffset(months=3)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    transactions = transactions[transactions["Дата операции"].between(start_date, end_date)]
    transactions["День недели"] = transactions["Дата операции"].dt.day_name()
    transactions = transactions[transactions["Сумма платежа"] < 0]
    avg = transactions.groupby("День недели")["Сумма платежа"].mean().round(2)
    return pd.DataFrame(avg)


if __name__ == "__main__":
    df = read_xlsx()
    print(spending_by_weekday(df, date="12.12.2021"))
    # print(spending_by_weekday(df))
