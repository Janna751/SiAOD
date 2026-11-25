#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 5. Бинарное дерево поиска: обходы, вставка и удаление — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-05 и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST понадобится повторно в ДЗ 2
(Cases/kim-02-bst-height-experiment.md) — держите его чистым и переносимым.

Запуск: python lab05-bst-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
from collections import deque
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Бинарное дерево поиска (реализуется вручную, без сторонних библиотек)
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов ключей.

    Инвариант: для каждого узла все ключи левого поддерева меньше key,
    все ключи правого — больше. Ожидаемая сложность операций: TODO
    (выразить через высоту h и обосновать в отчёте).
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставка ключа; повторная вставка существующего ключа игнорируется."""
        if self.root is None:
            self.root = Node(key)
            return
        cur = self.root
        while True:
            if key < cur.key:
                if cur.left is None:
                    cur.left = Node(key)
                    return
                cur = cur.left
            elif key > cur.key:
                if cur.right is None:
                    cur.right = Node(key)
                    return
                cur = cur.right
            else:
                return

    def search(self, key: int) -> bool:
        """Возвращает True, если ключ есть в дереве."""
        cur = self.root
        while cur is not None:
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return True
        return False

    def delete(self, key: int) -> None:
        """Удаление ключа. Обработать три случая:

        1) лист — просто отцепить от родителя;
        2) один ребёнок — заменить узел его ребёнком;
        3) два ребёнка — заменить ключ преемником (минимум правого
           поддерева) и удалить преемника из правого поддерева.
        Отсутствующий ключ игнорируется.
        """
        cur = self.root
        parent: Node | None = None
        while cur is not None and cur.key != key:
            parent = cur
            if key < cur.key:
                cur = cur.left
            else:
                cur = cur.right
        if cur is None:
            return

        # Случай 3: два ребёнка — замена преемником (минимум правого поддерева)
        if cur.left is not None and cur.right is not None:
            succ_parent = cur
            succ = cur.right
            while succ.left is not None:
                succ_parent = succ
                succ = succ.left
            cur.key = succ.key
            cur = succ
            parent = succ_parent

        # У cur теперь 0 или 1 ребёнок
        child = cur.left if cur.left is not None else cur.right

        if parent is None:
            self.root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child
    # -- Обходы --------------------------------------------------------------

    def in_order(self) -> list[int]:
        """Симметричный обход (лево — узел — право): рекурсивно."""
        result: list[int] = []

        def rec(node: Node | None) -> None:
            if node is None:
                return
            rec(node.left)
            result.append(node.key)
            rec(node.right)

        rec(self.root)
        return result

    def pre_order(self) -> list[int]:
        """Прямой обход (узел — лево — право): рекурсивно."""
        result: list[int] = []

        def rec(node: Node | None) -> None:
            if node is None:
                return
            result.append(node.key)
            rec(node.left)
            rec(node.right)

        rec(self.root)
        return result

    def post_order(self) -> list[int]:
        """Обратный обход (лево — право — узел): рекурсивно."""
        result: list[int] = []

        def rec(node: Node | None) -> None:
            if node is None:
                return
            rec(node.left)
            rec(node.right)
            result.append(node.key)

        rec(self.root)
        return result

    def level_order(self) -> list[int]:
        """Обход в ширину по уровням: итеративно через очередь (deque)."""
        if self.root is None:
            return []
        result: list[int] = []
        q: deque[Node] = deque([self.root])
        while q:
            node = q.popleft()
            result.append(node.key)
            if node.left is not None:
                q.append(node.left)
            if node.right is not None:
                q.append(node.right)
        return result

    # -- Характеристики дерева ----------------------------------------------

    def height(self) -> int:
        """Высота дерева: число рёбер на самом длинном пути от корня.

        Пустое дерево имеет высоту -1, дерево из одного узла — 0.
        """

        def rec(node: Node | None) -> int:
            if node is None:
                return -1
            return 1 + max(rec(node.left), rec(node.right))

        return rec(self.root)

    def size(self) -> int:
        """Число узлов в дереве."""

        def rec(node: Node | None) -> int:
            if node is None:
                return 0
            return 1 + rec(node.left) + rec(node.right)

        return rec(self.root)


# ---------------------------------------------------------------------------
# 2. Верификация: инвариант BST и сверка с эталоном (docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def build(keys) -> BST:
    """Дерево, полученное последовательной вставкой keys в пустое BST."""
    tree = BST()
    for k in keys:
        tree.insert(k)
    return tree


def expect_search(tree: BST, key: int, present: bool, where: str) -> None:
    """search(key) обязан вернуть именно True или False."""
    got = tree.search(key)
    expect(got is present, f"{where}: search({key}) вернул {got!r}, ожидалось {present}")


TRAVERSALS = ("in_order", "pre_order", "post_order", "level_order")

# Деревья с известными обходами: идеальное дерево 4-2-6-1-3-5-7 (вставка по уровням)
# и пример лекции 5, где у узлов 10 и 14 по одному ребёнку.
KNOWN_TREES = {
    (4, 2, 6, 1, 3, 5, 7): {
        "in_order": [1, 2, 3, 4, 5, 6, 7],
        "pre_order": [4, 2, 1, 3, 6, 5, 7],
        "post_order": [1, 3, 2, 5, 7, 6, 4],
        "level_order": [4, 2, 6, 1, 3, 5, 7],
        "height": 2,
        "size": 7,
    },
    (8, 3, 10, 1, 6, 14, 4, 7, 13): {
        "in_order": [1, 3, 4, 6, 7, 8, 10, 13, 14],
        "pre_order": [8, 3, 1, 6, 4, 7, 10, 14, 13],
        "post_order": [1, 4, 7, 6, 3, 13, 14, 10, 8],
        "level_order": [8, 3, 10, 1, 6, 14, 4, 7, 13],
        "height": 3,
        "size": 9,
    },
}

# Удаление узла с двумя детьми: (ключи, удаляемый ключ, pre_order после замены
# преемником, pre_order после замены предшественником). В последних двух случаях
# у преемника (предшественника) есть свой ребёнок.
TWO_CHILDREN_CASES = [
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 3, [8, 4, 1, 6, 7, 10, 14, 13], [8, 1, 6, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 6, [8, 3, 1, 7, 4, 10, 14, 13], [8, 3, 1, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 8, [10, 3, 1, 6, 4, 7, 14, 13], [7, 3, 1, 6, 4, 10, 14, 13]),
    ((50, 30, 70, 60, 80, 65), 50, [60, 30, 70, 65, 80], [30, 70, 60, 65, 80]),
    ((50, 30, 70, 60, 80, 65), 70, [50, 30, 80, 60, 65], [50, 30, 65, 60, 80]),
]


def check_insert_search() -> None:
    """Поиск в пустом дереве, вставка, поиск есть/нет, повторная вставка."""
    tree = BST()
    expect_search(tree, 1, False, "пустое дерево")
    tree.insert(5)
    expect_search(tree, 5, True, "дерево из одного узла 5")
    expect_search(tree, 4, False, "дерево из одного узла 5")

    keys = [5, 2, 8, 1, 3, 9, 7]
    tree = build(keys)
    for k in range(11):
        expect_search(tree, k, k in keys, f"дерево из вставок {keys}")
    got = tree.in_order()
    expect(got == sorted(keys), f"in_order() после вставок {keys}: {got}, ожидалось {sorted(keys)}")
    tree.insert(5)
    tree.insert(1)
    got = tree.in_order()
    expect(got == sorted(keys), f"повторная вставка 5 и 1 изменила дерево: in_order() = {got}")


def check_traversals() -> None:
    """Четыре обхода: пустое дерево и деревья с известным ответом."""
    empty = BST()
    for name in TRAVERSALS:
        got = getattr(empty, name)()
        expect(got == [], f"{name}() пустого дерева: {got}, ожидалось []")
    for keys, answer in KNOWN_TREES.items():
        tree = build(keys)
        for name in TRAVERSALS:
            got = getattr(tree, name)()
            expect(got == answer[name],
                   f"{name}() дерева из вставок {list(keys)}: {got}, ожидалось {answer[name]}")


def check_height_size() -> None:
    """Высота в рёбрах (пустое дерево -1, один узел 0) и число узлов."""
    cases = [("пустое дерево", (), -1, 0), ("один узел 5", (5,), 0, 1)]
    cases += [(f"дерево из вставок {list(keys)}", keys, answer["height"], answer["size"])
              for keys, answer in KNOWN_TREES.items()]
    cases.append(("ключи 1, 2, …, 50 по возрастанию (цепочка)", tuple(range(1, 51)), 49, 50))
    for where, keys, height, size in cases:
        tree = build(keys)
        got_h, got_s = tree.height(), tree.size()
        expect(got_h == height, f"{where}: height() = {got_h}, ожидалось {height}")
        expect(got_s == size, f"{where}: size() = {got_s}, ожидалось {size}")


def check_delete() -> None:
    """Пустое дерево, лист, один ребёнок, корень с двумя детьми, отсутствующий и последний ключ."""
    tree = BST()
    tree.delete(1)  # удаление из пустого дерева не должно падать
    got = tree.in_order()
    expect(got == [], f"delete(1) из пустого дерева: in_order() = {got}")

    keys = [5, 2, 8, 1, 3]
    tree = build(keys)
    left = set(keys)
    steps = [(1, "лист 1"), (2, "узел 2 с одним ребёнком"), (5, "корень 5 с двумя детьми"),
             (4, "отсутствующий ключ 4"), (3, "ключ 3"), (8, "последний ключ 8")]
    for k, what in steps:
        tree.delete(k)
        left.discard(k)
        where = f"дерево из вставок {keys}, удаление: {what}"
        got = tree.in_order()
        expect(got == sorted(left), f"{where}: in_order() = {got}, ожидалось {sorted(left)}")
        expect_search(tree, k, False, where)
        for rest in left:
            expect_search(tree, rest, True, where)
    got_h, got_s = tree.height(), tree.size()
    expect(got_h == -1 and got_s == 0,
           f"после удаления всех ключей: height() = {got_h}, size() = {got_s}, ожидалось -1 и 0")


def check_delete_two_children() -> None:
    """Узел с двумя детьми получает ключ преемника (или предшественника): форму дерева
    после удаления однозначно показывает pre_order()."""
    for keys, k, by_successor, by_predecessor in TWO_CHILDREN_CASES:
        tree = build(keys)
        tree.delete(k)
        where = f"delete({k}) в дереве из вставок {list(keys)}"
        rest = sorted(set(keys) - {k})
        got = tree.in_order()
        expect(got == rest, f"{where}: in_order() = {got}, ожидалось {rest}")
        got = tree.pre_order()
        expect(got in (by_successor, by_predecessor),
               f"{where}: pre_order() = {got}; при замене преемником ожидалось {by_successor}, "
               f"предшественником — {by_predecessor}")


def check_against_reference() -> None:
    """Случайные команды insert/delete: после каждой in_order() совпадает с sorted(эталона)."""
    rng = random.Random(0)
    for run in range(1, 101):
        tree = BST()
        etalon: set[int] = set()
        for step in range(1, rng.randint(1, 80) + 1):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                tree.insert(k)
                etalon.add(k)
                op = f"insert({k})"
            else:
                tree.delete(k)
                etalon.discard(k)
                op = f"delete({k})"
            # Инвариант BST: in-order даёт строго возрастающую последовательность ключей
            got = tree.in_order()
            expect(got == sorted(etalon), f"прогон {run}, команда №{step} {op}: "
                                          f"in_order() = {got}, эталон {sorted(etalon)}")
        where = f"прогон {run}, итоговое дерево"
        for k in range(-30, 31):
            expect_search(tree, k, k in etalon, where)
        n = len(etalon)
        got = tree.size()
        expect(got == n, f"{where}: size() = {got}, эталон {n}")
        for name in TRAVERSALS[1:]:
            got = getattr(tree, name)()
            expect(sorted(got) == sorted(etalon), f"{where}: {name}() содержит не те ключи: {got}")
        got = tree.height()
        low, high = (-1, -1) if n == 0 else (n.bit_length() - 1, n - 1)
        expect(low <= got <= high,
               f"{where}: height() = {got} при {n} узлах, возможно от {low} до {high}")

def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    checks = (
        ("вставка и поиск", check_insert_search),
        ("обходы", check_traversals),
        ("высота и размер", check_height_size),
        ("удаление", check_delete),
        ("удаление узла с двумя детьми", check_delete_two_children),
        ("сверка с эталоном set/sorted", check_against_reference),
    )
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")

    def check_invariant() -> None:
        def ok(node: Node | None, lo: int | None, hi: int | None) -> None:
            if node is None:
                return
            if lo is not None:
                expect(node.key > lo, f"инвариант BST нарушен: {node.key} <= {lo}")
            if hi is not None:
                expect(node.key < hi, f"инвариант BST нарушен: {node.key} >= {hi}")
            ok(node.left, lo, node.key)
            ok(node.right, node.key, hi)

        for keys, _ in KNOWN_TREES.items():
            tree = build(keys)
            ok(tree.root, None, None)
        print("  инвариант BST: OK")

    check_invariant()

    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк: поиск в BST против поиска в списке (docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
QUERIES = 1_000  # число поисков на один замер


def bench(fn) -> float:
    """Медиана времени выполнения fn() по REPEATS запускам, с прогревом."""
    fn()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Сравнение времени QUERIES поисков в BST и в списке (оператор in)."""
    rng = random.Random(seed)
    print(f"{'n':>8} {'h(BST)':>7} {'t_bst, c':>10} {'t_list, c':>10}")

    n_list, h_list, t_bst_list, t_list_list = [], [], [], []

    for n in SIZES:
        keys = rng.sample(range(10 * n), n)
        queries = [rng.randint(0, 10 * n) for _ in range(QUERIES)]
        tree = BST()
        for k in keys:
            tree.insert(k)

        def search_bst() -> None:
            for q in queries:
                tree.search(q)

        def search_list() -> None:
            for q in queries:
                q in keys

        t_bst = bench(search_bst)
        t_list = bench(search_list)
        h = tree.height()

        print(f"{n:>8} {h:>7} {t_bst:>10.6f} {t_list:>10.6f}")

        n_list.append(n)
        h_list.append(h)
        t_bst_list.append(t_bst)
        t_list_list.append(t_list)

    plot_benchmark(n_list, h_list, t_bst_list, t_list_list)
    # TODO: оформить результаты таблицей/графиком в отчёте;
    # TODO: сопоставить рост t_bst с высотой дерева, а t_list — с n;
    # TODO: в отчёте объяснить деградацию BST на упорядоченных ключах
    #       и гарантию высоты AVL-дерева (не более 1,44*log2(n)) — мостик к ДЗ 2.

def plot_benchmark(n_list, h_list, t_bst_list, t_list_list) -> None:
    """Построение графика сравнения BST и списка в логарифмической шкале."""
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Левая ось — время поиска (log-log)
    ax1.set_xlabel("n (число узлов)")
    ax1.set_ylabel("Время поиска 1000 запросов, с", color="black")
    ax1.plot(n_list, t_bst_list, "o-", label="BST (t_bst)", color="blue", linewidth=2)
    ax1.plot(n_list, t_list_list, "s-", label="Список (t_list)", color="red", linewidth=2)
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.grid(True, which="both", ls="--", alpha=0.4)

    # Правая ось — высота дерева (линейная)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Высота h(BST)", color="black")
    ax2.plot(n_list, h_list, "^-", label="h(BST)", color="green", linewidth=2)
    ax2.set_yscale("linear")

    # Легенды
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Поиск в BST vs список")
    plt.tight_layout()
    plt.savefig("bst_benchmark.png", dpi=150)
    print("График сохранён: bst_benchmark.png")
    plt.show()

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant  # seed по варианту — см. docs/reproducibility.md
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
