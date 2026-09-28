"""
Чтение Excel-файла (Наименование | Величина) и конвертация в CSV,
который затем передаётся алгоритму (algorithm.py).
"""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ["Наименование", "Величина"]


def read_excel(xlsx_path: str) -> pd.DataFrame:
    """Читает Excel-файл и возвращает DataFrame с колонками Наименование/Величина."""
    df = pd.read_excel(xlsx_path)

    # приводим названия колонок к ожидаемым (на случай лишних пробелов/регистра)
    df.columns = [str(c).strip() for c in df.columns]

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(
                f"В Excel-файле отсутствует обязательная колонка '{col}'. "
                f"Найдены колонки: {list(df.columns)}"
            )

    df = df[REQUIRED_COLUMNS].dropna()
    df["Величина"] = pd.to_numeric(df["Величина"], errors="coerce")
    df = df.dropna(subset=["Величина"])
    df["Наименование"] = df["Наименование"].astype(str)

    return df.reset_index(drop=True)


def excel_to_csv(xlsx_path: str, csv_path: str) -> str:
    """Читает Excel и сохраняет CSV с теми же данными. Возвращает путь к CSV."""
    df = read_excel(xlsx_path)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def read_csv(csv_path: str) -> pd.DataFrame:
    """Читает CSV (в формате, созданном excel_to_csv) для передачи в алгоритм."""
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df.columns = [str(c).strip() for c in df.columns]
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"В CSV отсутствует колонка '{col}'")
    df["Величина"] = pd.to_numeric(df["Величина"], errors="coerce")
    df = df.dropna(subset=["Величина"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    import sys

    xlsx = sys.argv[1] if len(sys.argv) > 1 else "data/input.xlsx"
    csv_out = sys.argv[2] if len(sys.argv) > 2 else "data/input.csv"
    path = excel_to_csv(xlsx, csv_out)
    print(f"CSV сохранён: {path}")
