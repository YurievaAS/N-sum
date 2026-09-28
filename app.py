"""
Веб-интерфейс:
  - показывает текущий список из Excel (Наименование | Величина)
  - позволяет загрузить свой Excel-файл (заменяет текущий список)
  - принимает N (сумма) и погрешность в % (по умолчанию 2, только в плюс)
  - вызывает excel_reader (Excel -> CSV) и algorithm (DP) и показывает
    до 5 лучших найденных комбинаций, либо сообщение "нет подходящих комбинаций"
"""

from __future__ import annotations

import os

from flask import Flask, render_template, request, redirect, url_for, flash

from excel_reader import excel_to_csv, read_csv
from algorithm import find_best_combinations

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
XLSX_PATH = os.path.join(DATA_DIR, "input.xlsx")
CSV_PATH = os.path.join(DATA_DIR, "input.csv")

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # для flash-сообщений, менять не обязательно для локального демо


def ensure_csv_exists() -> None:
    """Если CSV ещё не сгенерирован из текущего Excel — генерируем."""
    if os.path.exists(XLSX_PATH) and not os.path.exists(CSV_PATH):
        excel_to_csv(XLSX_PATH, CSV_PATH)


def reload_from_xlsx() -> None:
    """
    Принудительно перечитывает XLSX_PATH и перегенерирует CSV, даже если он
    уже существует. Используется кнопкой "Обновить список", чтобы подхватить
    изменения в файле по тому же пути (например, если файл на диске был
    заменён/перезаписан снаружи) без повторной загрузки через форму.
    """
    if not os.path.exists(XLSX_PATH):
        raise FileNotFoundError(f"Файл {XLSX_PATH} не найден")
    excel_to_csv(XLSX_PATH, CSV_PATH)


def load_current_rows() -> list[tuple[str, float]]:
    ensure_csv_exists()
    if not os.path.exists(CSV_PATH):
        return []
    df = read_csv(CSV_PATH)
    return list(zip(df["Наименование"], df["Величина"]))


@app.route("/", methods=["GET"])
def index():
    rows = load_current_rows()
    total_sum = sum(v for _, v in rows) if rows else 0
    return render_template(
        "index.html",
        rows=rows,
        total_sum=total_sum,
        combos=None,
        target_n=None,
        epsilon=2,
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("excel_file")
    if not file or file.filename == "":
        flash("Файл не выбран")
        return redirect(url_for("index"))

    file.save(XLSX_PATH)
    # перегенерируем CSV из нового Excel (шаг 3: Excel -> CSV -> алгоритм)
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)
    excel_to_csv(XLSX_PATH, CSV_PATH)
    flash("Файл успешно загружен и обновлён")
    return redirect(url_for("index"))


@app.route("/refresh", methods=["POST"])
def refresh():
    """
    Перечитывает текущий Excel-файл (тот же путь) заново — не требует выбора
    файла. Удобно, если файл на диске был перезаписан новой версией под тем
    же именем.
    """
    try:
        reload_from_xlsx()
        flash("Список перечитан из файла")
    except FileNotFoundError as exc:
        flash(str(exc))
    return redirect(url_for("index"))


@app.route("/calculate", methods=["POST"])
def calculate():
    rows = load_current_rows()
    total_sum = sum(v for _, v in rows) if rows else 0

    error = None
    combos = None
    target_n = request.form.get("target_n", "").strip()
    epsilon_raw = request.form.get("epsilon", "").strip()

    try:
        target_n_val = float(target_n.replace(",", "."))
        epsilon_val = float(epsilon_raw.replace(",", ".")) if epsilon_raw else 2.0

        combos = find_best_combinations(
            rows,
            target_n=target_n_val,
            epsilon_percent=epsilon_val,
            max_results=5,
        )
    except ValueError as exc:
        error = f"Некорректный ввод: {exc}"
        target_n_val = None
        epsilon_val = 2.0

    return render_template(
        "index.html",
        rows=rows,
        total_sum=total_sum,
        combos=combos,
        target_n=target_n,
        epsilon=epsilon_raw or 2,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050, use_reloader=False)
