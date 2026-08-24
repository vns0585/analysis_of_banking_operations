import pandas as pd


def read_xlsx(path: str = "data/operations.xlsx") -> pd.DataFrame:
    return pd.read_excel(path)
