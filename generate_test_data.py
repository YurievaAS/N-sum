"""
Генерирует тестовый Excel-файл (data/input.xlsx) со столбцами:
    Наименование | Величина

По умолчанию создаёт 200 записей со случайными именами и суммами.
Запуск:
    python generate_test_data.py [--count 200] [--out data/input.xlsx]
"""

import argparse
import random

import pandas as pd

FIRST_NAMES = [
    "Иван", "Пётр", "Сергей", "Алексей", "Дмитрий", "Николай", "Андрей",
    "Михаил", "Владимир", "Артём", "Мария", "Анна", "Елена", "Ольга",
    "Татьяна", "Наталья", "Ирина", "Светлана", "Екатерина", "Юлия",
]

LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов",
    "Соколов", "Лебедев", "Козлов", "Новиков", "Морозов", "Волков",
    "Алексеев", "Захаров", "Егоров", "Павлов", "Козлова", "Степанова",
    "Николаева", "Орлова",
]


def generate(count: int, min_value: int, max_value: int, seed: int | None) -> pd.DataFrame:
    if seed is not None:
        random.seed(seed)

    rows = []
    used_names = set()
    for _ in range(count):
        while True:
            name = f"{random.choice(LAST_NAMES)} {random.choice(FIRST_NAMES)}"
            # допускаем повторы фамилия+имя, но добавляем порядковый номер, если уже было
            if name not in used_names:
                used_names.add(name)
                break
            name = f"{name} ({len(used_names) + 1})"
            used_names.add(name)
            break
        value = random.randint(min_value, max_value)
        rows.append({"Наименование": name, "Величина": value})

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Генерация тестового Excel-файла")
    parser.add_argument("--count", type=int, default=250, help="Количество записей")
    parser.add_argument("--min", dest="min_value", type=int, default=1, help="Мин. величина")
    parser.add_argument("--max", dest="max_value", type=int, default=100, help="Макс. величина")
    parser.add_argument("--out", type=str, default="data/input.xlsx", help="Путь к выходному файлу")
    parser.add_argument("--seed", type=int, default=42, help="Seed для воспроизводимости")
    args = parser.parse_args()

    df = generate(args.count, args.min_value, args.max_value, args.seed)
    df.to_excel(args.out, index=False)
    print(f"Создан файл {args.out} с {len(df)} записями.")
    print(f"Сумма всех величин: {df['Величина'].sum()}")


if __name__ == "__main__":
    main()
