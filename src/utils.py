import json

import pandas as pd


def read_xlsx(path: str = "data/operations.xlsx") -> pd.DataFrame:
    """Принимает путь к файлу с транзакциями в формате xlsx, возвращает DataFrame"""
    try:
        return pd.read_excel(path)
    except Exception:
        return pd.DataFrame()


def get_user_settings() -> dict:
    """Возвращает настройки пользователя из файла user_settings.json"""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as json_file:
            result = json.load(json_file)
            if not isinstance(result, dict):
                return {}
            return result
    except Exception:
        return {}
