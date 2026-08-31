import json
import os
from bisect import bisect
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import get_user_settings, read_xlsx

load_dotenv()


def get_greeting() -> str:
    """Возвращает приветствие, соответствующее текущему времени"""
    hour = datetime.now().hour
    boundaries = [0, 6, 12, 18]
    greetings = ["Доброй ночи", "Доброе утро", "Добрый день", "Добрый вечер"]
    return greetings[bisect(boundaries, hour) - 1]


def get_cards(df: pd.DataFrame) -> list[dict]:
    """Возвращает список словарей с расходами по каждой карте и потенциальный кэшбэк по ней"""
    try:
        df = df[["Номер карты", "Сумма платежа", "Кэшбэк"]]
    except KeyError:
        return []
    df["Номер карты"] = df["Номер карты"].str[-4:]
    data = df[df["Сумма платежа"] < 0].groupby("Номер карты")["Сумма платежа"].sum().round(2).to_dict()
    result = []
    for key, value in data.items():
        result.append(
            {
                "last_digits": key,
                "total_spent": value*(-1),
                "cashback": round(value*(-0.01), 2)
            }
        )
    return result


def get_top_transactions(df: pd.DataFrame) -> list[dict]:
    """Возвращает топ-5 транзакций отсортированных по убыванию поля amount"""
    try:
        df = df[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    except KeyError:
        return []
    df.columns = ["date", "amount", "category", "description"]
    df.sort_values(by="amount", ascending=False, inplace=True)
    try:
        df["date"] = df["date"].dt.strftime("%d.%m.%Y")
    except AttributeError:
        return []
    return df.head(5).astype(object).where(pd.notna(df), None).to_dict("records")


def get_currency_rates() -> list[dict]:
    """Возвращает текущий курс валют, для валют из файла настроек пользователя"""
    user_settings = get_user_settings()
    if user_settings == {}:
        return []
    currency_apikey = os.getenv("CURRENCY_API_KEY")
    params = {
        "get": "rates",
        "pairs": ",".join([currency + "RUB" for currency in user_settings.get("user_currencies", [])]),
        "key": currency_apikey
    }
    response = requests.get("https://currate.ru/api/", params=params)
    currency_rates = []
    if response.status_code != 200:
        return []
    for key, value in response.json()["data"].items():
        currency_rates.append({"currency": key.replace("RUB", ""), "rate": round(float(value), 2)})
    return currency_rates


def get_stock_prices() -> list[dict]:
    """Возвращает текущие цены на акции из SP500, для акций из файла настроек пользователя"""
    user_settings = get_user_settings()
    if user_settings == {}:
        return []
    stock_apikey = os.getenv("STOCK_API_KEY")
    if stock_apikey is not None:
        headers = {"X-Api-Key": stock_apikey}
    else:
        headers = {}
    stock_prices = []
    for stock in user_settings.get("user_stocks", {}):
        params = {"ticker": stock}
        response = requests.get("https://api.api-ninjas.com/v1/stockprice", headers=headers, params=params)
        if response.status_code == 200:
            stock_prices.append({"stock": stock, "price": response.json()["price"]})
        else:
            stock_prices.append({})
    return stock_prices


def process_data(date: str) -> str:
    """Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    с приветствием, расходами по картам, топ-5 операций, курсы валют и цены акций из файла настроек пользователя.
    Данные берутся за период с начала месяца по переданную дату включительно."""
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df = read_xlsx()
    if df.empty:
        return json.dumps({})
    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        df = df[df["Дата операции"].between(start_date, end_date)]
    except KeyError:
        return json.dumps({})
    processed_data = {
        "greeting": get_greeting(),
        "cards": get_cards(df),
        "top_transactions": get_top_transactions(df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices()
    }
    return json.dumps(processed_data, ensure_ascii=False, indent=4)
