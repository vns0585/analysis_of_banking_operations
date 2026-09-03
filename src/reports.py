import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/reports.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def report(path: str = "report.txt") -> Callable:
    """Декоратор записывающий результаты работы функции в файл"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = str(func(*args, **kwargs))
                logger.debug(f"Получен результат функции {func.__name__}: {result}")
            except Exception as e:
                logger.error(f"В переданной функции {func.__name__} произошла ошибка: {type(e).__name__}")
                raise e
            try:
                with open(path, "w", encoding="utf-8") as file:
                    file.write(result)
            except Exception as e:
                logger.error(f"Результат функции {func.__name__} не был записан в файл {path}."
                             f" Ошибка: {type(e).__name__}")
            else:
                logger.debug(f"Результат функции {func.__name__} успешно записан в файл {path}")
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
        logger.warning("Переданные транзакции пусты, либо отсутствуют колонки \"Дата операции\", \"Сумма платежа\"")
        return pd.DataFrame()
    if date is None:
        logger.info("Дата не передана, используется текущая дата")
        end_date = datetime.today()
    else:
        logger.info(f"Получена дата: {date}")
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
    weekdays = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }
    avg_sorted_df["День недели"] = avg_sorted_df["День недели"].replace(weekdays)
    return avg_sorted_df
