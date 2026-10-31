#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: TODO (обосновать в отчёте).

    Подсказка: досрочный выход, если за проход не было ни одного обмена, —
    именно он даёт лучший случай на упорядоченном входе.
    """
    a = list(a)  # работаем с копией
    n = len(a)
    comparisons = 0
    swaps = 0

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:  # досрочный выход — лучший случай O(n)
            break

    return a, comparisons, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Лучший случай O(n), худший O(n²)."""
    a = list(a)  # работаем с копией
    n = len(a)
    comparisons = 0
    shifts = 0  # перемещения (сдвиги)

    for i in range(1, n):
        key = a[i]
        j = i - 1

        # Сдвигаем элементы вправо, пока они больше key
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break

        # Если вышли из цикла потому что j < 0, нужно учесть последнее сравнение
        # Но в нашей логике сравнение уже посчитано выше
        a[j + 1] = key
        if j + 1 != i:  # если элемент действительно сдвинулся.
            shifts += 1  # финальная вставка key

    return a, comparisons, shifts

def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Ожидаемая сложность: TODO (почему не зависит от входа?)."""
    """Сортировка выбором. Сложность Θ(n²) на любом входе."""
    a = list(a)  # работаем с копией
    n = len(a)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1

    return a, comparisons, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.
    Ожидаемая сложность: в среднем TODO, в худшем случае TODO (обосновать
    в отчёте, объяснить роль рандомизации). rng передаётся снаружи, чтобы
    запуск был воспроизводим по seed варианта.
    """

    if rng is None:
        rng = random.Random()

    # Внутренняя рекурсивная функция
    def _quick_sort(arr, lo, hi):
        if lo >= hi:
            return

        # Выбираем опорный элемент случайно
        pivot_idx = rng.randrange(lo, hi)
        pivot = arr[pivot_idx]

        # Разбиение на три части: меньше, равные, больше
        less = []
        equal = []
        greater = []

        for i in range(lo, hi):
            if arr[i] < pivot:
                less.append(arr[i])
            elif arr[i] == pivot:
                equal.append(arr[i])
            else:
                greater.append(arr[i])
        # Копируем обратно в массив
        idx = lo
        for x in less:
            arr[idx] = x
            idx += 1
        for x in equal:
            arr[idx] = x
            idx += 1
        for x in greater:
            arr[idx] = x
            idx += 1

        # Рекурсивно сортируем меньшую и большую части
        _quick_sort(arr, lo, lo + len(less))
        _quick_sort(arr, lo + len(less) + len(equal), hi)

    # Работаем с копией, чтобы не менять входной список
    result = list(a)
    _quick_sort(result, 0, len(result))
    return result



# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """


    """Показать, какие из четырёх сортировок стабильны."""


    # Класс для пар (ключ, метка) с сравнением только по ключу
    class Pair:
        def __init__(self, key, label):
            self.key = key
            self.label = label

        def __lt__(self, other):
            return self.key < other.key

        def __repr__(self):
            return f"({self.key}, '{self.label}')"


    # Исходный массив с повторяющимися ключами
    original = [
        Pair(2, "a"),
        Pair(1, "b"),
        Pair(2, "c"),
        Pair(1, "d"),
        Pair(2, "e"),
    ]

    print("\n=== Демонстрация стабильности сортировок ===")
    print(f"Исходный массив: {original}")
    print(f"Ожидаемый порядок меток при ключах 1: b, d")
    print(f"Ожидаемый порядок меток при ключах 2: a, c, e\n")

    # Тестируем каждую сортировку
    algorithms = [
        ("bubble_sort", lambda a: bubble_sort(a)[0]),
        ("insertion_sort", lambda a: insertion_sort(a)[0]),
        ("selection_sort", lambda a: selection_sort(a)[0]),
        ("quick_sort", lambda a: quick_sort(a, random.Random(0))),
    ]

    for name, fn in algorithms:
        # Создаём свежую копию для каждой сортировки
        test_data = [Pair(p.key, p.label) for p in original]
        sorted_data = fn(test_data)

        # Извлекаем порядок меток
        labels = [p.label for p in sorted_data]

        # Проверяем стабильность
        # Для ключа 1: метки должны быть в порядке b, d
        # Для ключа 2: метки должны быть в порядке a, c, e
        key_1_labels = [p.label for p in sorted_data if p.key == 1]
        key_2_labels = [p.label for p in sorted_data if p.key == 2]

        stable = (key_1_labels == ["b", "d"] and key_2_labels == ["a", "c", "e"])

        print(f"{name}:")
        print(f"  Результат: {sorted_data}")
        print(f"  Метки при ключе 1: {key_1_labels}")
        print(f"  Метки при ключе 2: {key_2_labels}")
        print(f"  Стабильна: {'ДА' if stable else 'НЕТ'}\n")

# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    import matplotlib.pyplot as plt

    plans = [
        ("bubble_sort", bubble_sort, SIZES_QUADRATIC),
        ("insertion_sort", insertion_sort, SIZES_QUADRATIC),
        ("selection_sort", selection_sort, SIZES_QUADRATIC),
        ("quick_sort", lambda a: (quick_sort(a, random.Random(seed)), 0, 0), SIZES_QUICK),
    ]

    for name, fn, sizes in plans:
        print(f"\n{name}:")
        times_data = {"упорядоченный": [], "случайный": [], "обратный": []}

        # 1. Вывод счётчиков операций для первого размера (для отчёта)
        n_counters = sizes[0]
        print(f"  --- Счётчики операций для n={n_counters} ---")
        for cls, data in make_inputs(n_counters, seed).items():
            res, comps, moves = fn(list(data))
            print(f"    вход={cls:<13}: сравнений={comps:>8}, перемещений/обменов={moves:>8}")

        # 2. Замер времени выполнения
        for n in sizes:
            inputs = make_inputs(n, seed)
            for cls, data in inputs.items():
                # Для замера времени используем обёртку, которая берёт только первый элемент кортежа
                t = bench(lambda x: fn(x)[0], data)
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
                times_data[cls].append(t)

        # 3. Построение log-log графика
        plt.figure(figsize=(8, 6))
        for cls, times in times_data.items():
            plt.loglog(sizes, times, marker='o', label=cls)

        plt.xlabel("Размер массива (n)")
        plt.ylabel("Время выполнения (сек)")
        plt.title(f"Зависимость времени от n для {name} (log-log)")
        plt.legend()
        plt.grid(True, which="both", ls="--")
        plt.xticks(sizes, labels=[str(s) for s in sizes])

        # Сохраняем график в файл
        filename = f"plot_{name}.png"
        plt.savefig(filename)
        print(f"График сохранён как {filename}")
        plt.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
