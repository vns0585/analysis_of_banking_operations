import json
import os
import logging
import pandas as pd


os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def read_xlsx(path: str = "data/operations.xlsx") -> pd.DataFrame:
    """Принимает путь к файлу с транзакциями в формате xlsx, возвращает DataFrame"""
    try:
        return pd.read_excel(path)
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении файла: {type(e).__name__}")
        return pd.DataFrame()

def get_user_settings() -> dict:
    """Возвращает настройки пользователя из файла user_settings.json"""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as json_file:
            result = json.load(json_file)
            if not isinstance(result, dict):
                logger.warning("Неожиданный формат файла настроек user_settings.json")
                return {}
            logger.debug("Настройки пользователя успешно получены")
            return result
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении файла: {type(e).__name__}")
        return {}
