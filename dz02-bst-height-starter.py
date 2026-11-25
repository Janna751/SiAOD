#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 (Cases) и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST из ЛР 5 рекомендуется подключить как
модуль; ниже дан минимальный узел и сигнатуры на случай автономного запуска.

Запуск: python dz02-bst-height-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
import math
from collections import deque
from pathlib import Path
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
#    Внимание: на упорядоченном потоке дерево вырождается в список глубиной
#    до 10^4, поэтому вставка и обходы должны быть итеративными —
#    рекурсивные варианты вызовут RecursionError.
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень дерева.

    Дубликаты игнорируются (ключи в эксперименте уникальны).
    """
    node = Node(key)
    if root is None:
        return node
    cur = root
    while True:
        if key < cur.key:
            if cur.left is None:
                cur.left = node
                return root
            cur = cur.left
        elif key > cur.key:
            if cur.right is None:
                cur.right = node
                return root
            cur = cur.right
        else:  # дубликат игнорируем
            return root


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------


def tree_height(root: Node | None) -> int:
    """Высота дерева: число рёбер на самом длинном пути от корня до листа.

    Пустое дерево: -1; один узел: 0. Реализовать итеративно
    (обход в ширину или в глубину с явным стеком/очередью).
    """
    if root is None:
        return -1
    q: deque[Node] = deque([root])
    h = -1
    while q:                      # обход по уровням, h = номер последнего уровня
        h += 1
        for _ in range(len(q)):
            node = q.popleft()
            if node.left is not None:
                q.append(node.left)
            if node.right is not None:
                q.append(node.right)
    return h


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно."""
    if root is None:
        return 0
    stack: list[tuple[Node, int]] = [(root, 0)]
    total = 0
    while stack:
        node, d = stack.pop()
        total += d
        if node.right is not None:
            stack.append((node.right, d + 1))
        if node.left is not None:
            stack.append((node.left, d + 1))
    return total


def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно."""
    if root is None:
        return 0
    stack: list[Node] = [root]
    cnt = 0
    while stack:
        node = stack.pop()
        cnt += 1
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return cnt


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла: sum_depths / count_nodes (0.0 для пустого)."""
    n = count_nodes(root)
    return sum_depths(root) / n if n else 0.0


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком) — для верификации."""
    keys: list[int] = []
    stack: list[Node] = []
    cur = root
    while stack or cur is not None:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        keys.append(cur.key)
        cur = cur.right
    return keys


# ---------------------------------------------------------------------------
# 3. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    # Граничные случаи: пустое дерево и один узел
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1

    # Типовой случай: [2, 1, 3] — идеально сбалансированное дерево из 3 узлов
    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2  # 0 (корень) + 1 + 1

    # Вырожденный случай: упорядоченные ключи 1..n дают "список"
    n = 100
    degenerate = build_bst(list(range(1, n + 1)))
    assert tree_height(degenerate) == n - 1
    assert avg_depth(degenerate) == (n - 1) / 2  # (0+1+...+(n-1)) / n

    # Сверка с эталоном стандартной библиотеки: инвариант BST —
    # in-order-обход совпадает с sorted() на случайных наборах ключей
    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и каркас замеров (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]  # геометрический шаг, n до 10^4
REPEATS = 5


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей (детерминированно по seed варианта)."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n — худший поток вставок для BST."""
    return list(range(1, n + 1))


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""

    def run() -> None:
        for q in queries:
            node = root
            while node is not None and node.key != q:
                node = node.left if q < node.key else node.right

    run()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_experiment(seed: int) -> None:
    """Таблица замеров + графики h(n) и средней глубины."""
    rng = random.Random(seed)
    rows: list[tuple] = []
    h_r, h_o, d_r, d_o = [], [], [], []
    log_ref = [math.log2(n) for n in SIZES]

    print(f"{'n':>7} {'h_случ':>8} {'d_случ':>8} {'h_упор':>8} "
          f"{'d_упор':>8} {'log2(n)':>8} {'h/log2':>8} "
          f"{'t_случ,мс':>10} {'t_упор,мс':>10} {'t_уп/t_сл':>10}")

    for n in SIZES:
        keys_r = random_keys(n, rng)
        root_r = build_bst(keys_r)
        root_o = build_bst(ordered_keys(n))

        hr, ho = tree_height(root_r), tree_height(root_o)
        dr, do = avg_depth(root_r), avg_depth(root_o)
        lg = math.log2(n)

        # Успешный поиск: одинаковое ЧИСЛО запросов, ключи каждого дерева,
        # порядок запросов перемешан (чтобы не кэшировать один путь).
        q_r = keys_r[:]; rng.shuffle(q_r)
        q_o = ordered_keys(n); rng.shuffle(q_o)
        tr = bench_search(root_r, q_r)
        to = bench_search(root_o, q_o)

        h_r.append(hr); h_o.append(ho); d_r.append(dr); d_o.append(do)
        rows.append((n, hr, dr, ho, do, lg, tr, to))
        print(f"{n:>7} {hr:>8} {dr:>8.2f} {ho:>8} {do:>8.2f} {lg:>8.2f} "
              f"{hr / lg:>8.2f} {tr * 1e3:>10.3f} {to * 1e3:>10.3f} "
              f"{to / tr:>10.1f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(f"BST: высота и средняя глубина (seed={seed})")

    ax1.plot(SIZES, h_r, "o-", label="h случайный поток")
    ax1.plot(SIZES, h_o, "s-", label="h упорядоченный поток")
    ax1.plot(SIZES, log_ref, "--", color="gray", label="log₂(n)")
    ax1.plot(SIZES, [4.311 * math.log(n) for n in SIZES], "-.", color="green",
             label="4.311·ln(n) — E[h] случайного BST")
    ax1.plot(SIZES, SIZES, ":", color="red", label="n")
    ax1.set(xlabel="n", ylabel="высота h (рёбра)", xscale="log", yscale="log",
            title="Высота h(n)")
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend(fontsize=8)

    ax2.plot(SIZES, d_r, "o-", label="d̄ случайный поток")
    ax2.plot(SIZES, d_o, "s-", label="d̄ упорядоченный поток")
    ax2.plot(SIZES, log_ref, "--", color="gray", label="log₂(n)")
    ax2.plot(SIZES, [(n - 1) / 2 for n in SIZES], ":", color="red",
             label="(n−1)/2")
    ax2.set(xlabel="n", ylabel="средняя глубина узла", xscale="log",
            yscale="log", title="Средняя глубина d̄(n)")
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend(fontsize=8)

    fig.tight_layout()
    out = Path(f"bst_height_seed{seed}.png")
    fig.savefig(out, dpi=130)
    print(f"график сохранён: {out.resolve()}")
    plt.show()
        # TODO: замерить bench_search для обоих деревьев на одинаковых
        #       запросах и включить сравнение времени в отчёт
    # TODO: построить графики h(n) для обоих потоков на фоне log2(n) и n
    #       (matplotlib) и включить их в отчёт
    # TODO: в отчёте объяснить деградацию операций до O(n), привести справку
    #       об AVL (высота <= 1.44*log2(n), цена балансировки) и
    #       вывод-рекомендацию о выборе структуры


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


if __name__ == "__main__":
    main()
