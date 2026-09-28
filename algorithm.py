"""
Алгоритм подбора комбинации элементов (Наименование, Величина), сумма которых
попадает в диапазон [N; N * (1 + epsilon/100)] — то есть погрешность допускается
только В ПЛЮС от N.

Реализация — классическое ДП "0/1 рюкзак на достижимость суммы":
    dp[s] = (предыдущая_сумма, индекс_использованного_элемента) | None

Строим мапу достижимых сумм в диапазоне [0; target_max], после чего
восстанавливаем (backtracking) до 5 лучших (ближайших к N) комбинаций.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Item:
    index: int
    name: str
    value: float


@dataclass
class Combination:
    total: float
    excess_percent: float
    elements: list[Item] = field(default_factory=list)


NONE_MARKER = (-2, -2)   # ячейка ещё не достигнута
EMPTY_SET = (-1, -1)     # сумма 0 достигается пустым набором


def _scale_factor(values: list[float]) -> int:
    """100, если среди значений есть дробные, иначе 1 (работаем в целых числах)."""
    for v in values:
        if not float(v).is_integer():
            return 100
    return 1


def _build_dp(values_scaled: list[int], target_max: int) -> list[tuple[int, int]]:
    """
    dp[s] = (prev_sum, item_index), первый найденный путь к сумме s.
    Проход по каждому элементу — от target_max вниз до value, чтобы не
    использовать один и тот же элемент дважды (классика 0/1 knapsack).
    """
    dp = [NONE_MARKER] * (target_max + 1)
    dp[0] = EMPTY_SET

    for idx, v in enumerate(values_scaled):
        if v <= 0 or v > target_max:
            continue
        for s in range(target_max, v - 1, -1):
            if dp[s] != NONE_MARKER:
                continue
            prev = s - v
            if dp[prev] != NONE_MARKER:
                dp[s] = (prev, idx)

    return dp


def _reconstruct(dp: list[tuple[int, int]], items: list[Item], s: int) -> list[Item]:
    chosen = []
    while s != 0:
        prev, item_idx = dp[s]
        if (prev, item_idx) == NONE_MARKER:
            raise RuntimeError("Некорректное состояние DP при восстановлении пути")
        chosen.append(items[item_idx])
        s = prev
    chosen.reverse()
    return chosen


def find_best_combinations(
    rows: list[tuple[str, float]],
    target_n: float,
    epsilon_percent: float = 2.0,
    max_results: int = 5,
) -> list[Combination]:
    """
    rows: список (Наименование, Величина)
    target_n: искомая сумма N
    epsilon_percent: допустимая погрешность В ПЛЮС, в процентах (по умолчанию 2)
    max_results: сколько лучших комбинаций вернуть (по умолчанию 5)

    Возвращает список Combination, отсортированный по возрастанию превышения
    над N (самые "выгодные" — то есть ближе всего к N — первыми).
    Пустой список означает, что подходящих комбинаций не найдено.
    """
    if target_n <= 0:
        raise ValueError("N должно быть положительным числом")
    if epsilon_percent < 0:
        raise ValueError("Погрешность не может быть отрицательной")

    items = [Item(index=i, name=name, value=float(val)) for i, (name, val) in enumerate(rows)]
    if not items:
        return []

    values = [it.value for it in items]
    scale = _scale_factor(values + [target_n])

    values_scaled = [int(round(v * scale)) for v in values]
    n_scaled = int(round(target_n * scale))
    target_max_scaled = int(math.floor(target_n * (1 + epsilon_percent / 100.0) * scale))

    if target_max_scaled < n_scaled:
        target_max_scaled = n_scaled  # защита от эпсилон=0 с округлением

    # ограничиваем DP только диапазоном [0; target_max] — суммы выше нам не нужны,
    # т.к. погрешность допускается только в плюс, не в минус
    dp = _build_dp(values_scaled, target_max_scaled)

    # ищем все достижимые суммы в [N; target_max], ближайшие к N — самые "выгодные"
    reachable_sums = [s for s in range(n_scaled, target_max_scaled + 1) if dp[s] != NONE_MARKER]

    if not reachable_sums:
        return []

    reachable_sums.sort(key=lambda s: s - n_scaled)  # по возрастанию превышения над N

    results: list[Combination] = []
    for s in reachable_sums:
        if len(results) >= max_results:
            break
        elements = _reconstruct(dp, items, s)
        total_real = s / scale
        excess_percent = (total_real - target_n) / target_n * 100.0
        results.append(Combination(total=total_real, excess_percent=excess_percent, elements=elements))

    return results


if __name__ == "__main__":
    # небольшой самотест
    demo_rows = [("A", 100), ("B", 250), ("C", 400), ("D", 999), ("E", 150), ("F", 600)]
    combos = find_best_combinations(demo_rows, target_n=800, epsilon_percent=5)
    if not combos:
        print("нет подходящих комбинаций")
    for c in combos:
        names = ", ".join(f"{e.name}({e.value})" for e in c.elements)
        print(f"sum={c.total:.2f}  excess={c.excess_percent:.2f}%  -> {names}")
