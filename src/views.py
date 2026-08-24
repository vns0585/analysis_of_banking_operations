from bisect import bisect
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from utils import read_xlsx

load_dotenv()


def get_greeting() -> str:
    """Возвращает приветствие, соответствующее текущему времени"""
    hour = datetime.now().hour
    boundaries = [0, 6, 12, 18]
    greetings = ["Доброй ночи", "Доброе утро", "Добрый день", "Добрый вечер"]
    return greetings[bisect(boundaries, hour) - 1]


def get_cards(df: pd.DataFrame) -> list[dict]:
    df = df[["Номер карты", "Сумма платежа", "Кэшбэк"]]
    df.columns = ["last_digits", "total_spent", "cashback"]
    df["last_digits"] = df["last_digits"].str[-4:]
    return df.astype(object).where(pd.notna(df), None).to_dict("records")


def get_top_transactions(df: pd.DataFrame) -> list[dict]:
    df = df[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
    df.columns = ["date", "amount", "category", "description"]
    df.sort_values(by="amount", ascending=False, inplace=True)
    return df.head(5).astype(object).where(pd.notna(df), None).to_dict("records")


def get_currency_rates() -> list[dict]:
    pass


def get_stock_prices() -> list[dict]:
    pass


def process_data(date: str) -> str:
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df = read_xlsx()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    df = df.query('@start_date <= `Дата операции` <= @end_date')

    processed_data = {
        "greeting": get_greeting(),
        "cards": get_cards(df),
        "top_transactions": get_top_transactions(df),
        "currency_rates": [],
        "stock_prices": []
    }
    return processed_data


if __name__ == "__main__":
    print(process_data("2021-12-31 00:00:00"))

