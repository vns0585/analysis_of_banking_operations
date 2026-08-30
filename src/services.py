import json

import pandas as pd

from src.utils import read_xlsx


def find_phone_numbers() -> str:
    """Возвращает json-ответ с транзакциями, в поле описание содержащими номера телефонов"""
    df = read_xlsx()
    if "Описание" not in df.columns or df.empty:
        result = pd.DataFrame()
    else:
        result = df[df["Описание"].str.contains(r"(?:\+7|8)\s*[\(-]?\d{3}[\)-]?\s*\d{3}\s*[-]?\d{2}\s*[-]?\d{2}")]
    return json.dumps(result.to_dict(orient="records"), ensure_ascii=False)
