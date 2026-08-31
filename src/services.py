import json
import os
import pandas as pd
import logging

from src.utils import read_xlsx


os.makedirs("logs", exist_ok=True)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/services.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def find_phone_numbers() -> str:
    """Возвращает json-ответ с транзакциями, в поле описание содержащими номера телефонов"""
    df = read_xlsx()
    if "Описание" not in df.columns or df.empty:
        logger.warning("Неожиданный формат файла Excel: Отсутствует столбец \"Описание\", либо файл пуст")
        result = pd.DataFrame()
    else:
        result = df[df["Описание"].str.contains(r"(?:\+7|8)\s*[\(-]?\d{3}[\)-]?\s*\d{3}\s*[-]?\d{2}\s*[-]?\d{2}")]
        logger.debug("Выборка транзакций с номерами телефонов в описании произведена успешно")
    return json.dumps(result.to_dict(orient="records"), ensure_ascii=False)
