from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd


def report(path: str = "report.txt") -> Callable:
    """Декоратор записывающий результаты работы функции в файл"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = str(func(*args, **kwargs))
            except Exception as e:
                raise e
            with open(path, "w", encoding="utf-8") as file:
                file.write(result)
            return result
        return wrapper
    return decorator


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает DataFrame со средним значением трат в каждый из дней недели
    за последние три месяца (от текущей или от переданной даты в формате YYYY-MM-DD HH:MM:SS)."""
    if (transactions.empty or
            "Дата операции" not in transactions.columns or
            "Сумма платежа" not in transactions.columns):
        return pd.DataFrame()
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
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    avg.index = pd.CategoricalIndex(avg.index, categories=day_order, ordered=True)
    avg_sorted = avg.sort_index()
    avg_sorted = avg_sorted.rename("Cредние траты")
    avg_sorted_df = avg_sorted.reset_index()
    avg_sorted_df["День недели"] = avg_sorted_df["День недели"].astype(str)
    return avg_sorted_df
