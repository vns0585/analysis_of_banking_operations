import json
import os
import logging
from bisect import bisect
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import get_user_settings, read_xlsx

load_dotenv()

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/views.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def get_greeting() -> str:
    """Возвращает приветствие, соответствующее текущему времени"""
    hour = datetime.now().hour
    logger.debug(f"Запрошено приветствие на {hour}:00")
    boundaries = [0, 6, 12, 18]
    greetings = ["Доброй ночи", "Доброе утро", "Добрый день", "Добрый вечер"]
    result = greetings[bisect(boundaries, hour) - 1]
    logger.debug(f"Возвращено приветствие: {result}")
    return result


def get_cards(df: pd.DataFrame) -> list[dict]:
    """Возвращает список словарей с расходами по каждой карте и потенциальный кэшбэк по ней"""
    try:
        df = df[["Номер карты", "Сумма платежа", "Кэшбэк"]]
    except KeyError as e:
        logger.error(f"В полученном DataFrame отсутствует один или несколько столбцов: \"Номер карты\","
                     f" \"Сумма платежа\", \"Кэшбэк\". Ошибка: {type(e).__name__}")
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
    except KeyError as e:
        logger.error(f"В полученном DataFrame отсутствует один или несколько столбцов: \"Дата операции\","
                     f" \"Сумма платежа\", \"Категория\", \"Описание\". Ошибка: {type(e).__name__}")
        return []
    df.columns = ["date", "amount", "category", "description"]
    df.sort_values(by="amount", ascending=False, inplace=True)
    try:
        df["date"] = df["date"].dt.strftime("%d.%m.%Y")
    except AttributeError as e:
        logger.error(f"Недопустимые данные в столбце \"Дата операции\". Ошибка: {type(e).__name__}")
        return []
    return df.head(5).astype(object).where(pd.notna(df), None).to_dict("records")


def get_currency_rates() -> list[dict]:
    """Возвращает текущий курс валют, для валют из файла настроек пользователя"""
    user_settings = get_user_settings()
    if user_settings == {}:
        logger.warning("Настройки пользователя пусты, либо не могут быть прочитаны.")
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
        logger.debug(f"Ошибка получения данных с API. Код ответа: {response.status_code}")
        return []
    for key, value in response.json()["data"].items():
        currency_rates.append({"currency": key.replace("RUB", ""), "rate": round(float(value), 2)})
    return currency_rates


def get_stock_prices() -> list[dict]:
    """Возвращает текущие цены на акции из SP500, для акций из файла настроек пользователя"""
    user_settings = get_user_settings()
    if user_settings == {}:
        logger.warning("Настройки пользователя пусты, либо не могут быть прочитаны.")
        return []
    stock_apikey = os.getenv("STOCK_API_KEY")
    if stock_apikey is not None:
        headers = {"X-Api-Key": stock_apikey}
    else:
        logger.warning("Невозможно загрузить STOCK_API_KEY. Проверьте переменные окружения.")
        headers = {}
    stock_prices = []
    for stock in user_settings.get("user_stocks", {}):
        params = {"ticker": stock}
        response = requests.get("https://api.api-ninjas.com/v1/stockprice", headers=headers, params=params)
        if response.status_code == 200:
            stock_prices.append({"stock": stock, "price": response.json()["price"]})
        else:
            logger.debug(f"Ошибка получения данных с API. Код ответа: {response.status_code}")
            stock_prices.append({})
    return stock_prices


def process_data(date: str) -> str:
    """Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    с приветствием, расходами по картам, топ-5 операций, курсы валют и цены акций из файла настроек пользователя.
    Данные берутся за период с начала месяца по переданную дату включительно."""
    logger.debug(f"Получена дата: {date}")
    end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    df = read_xlsx()
    if df.empty:
        logger.warning("Файл с транзакциями пуст, либо не может быть прочитан.")
        return json.dumps({})
    try:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        df = df[df["Дата операции"].between(start_date, end_date)]
    except KeyError as e:
        logger.error(f"Неожиданный формат Excel-файла. Отсутствует столбец \"Дата операции\"."
                     f" Ошибка: {type(e).__name__}")
        return json.dumps({})
    processed_data = {
        "greeting": get_greeting(),
        "cards": get_cards(df),
        "top_transactions": get_top_transactions(df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices()
    }
    return json.dumps(processed_data, ensure_ascii=False, indent=4)
