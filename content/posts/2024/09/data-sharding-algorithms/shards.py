#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import jump
import math
import bisect
import hashlib
import mmh3
from dataclasses import dataclass

import numpy as np
from tabulate import tabulate


def compare_shards(
    title: str, a_items: list[tuple[int, int]], b_items: list[tuple[int, int]]
):
    same_cnt = 0
    for a_i, b_i in zip(a_items, b_items):
        assert a_i[0] == b_i[0]
        same_cnt += 1 if a_i[1] == b_i[1] else 0

    shards_cnt_before = Counter([s for _, s in a_items])
    shards_cnt = Counter([s for _, s in b_items])
    shards = np.array(list(shards_cnt.values()))
    # print(shards)

    overlap = same_cnt / len(a_items) * 100
    return {
        "Title": title,
        "Overlap": overlap,
        "Shards (before)": len(shards_cnt_before),
        "Shards (after)": len(shards_cnt),
        "Items per shard": shards.mean(),
        "Items per shard (std)": shards.std(),
    }


def naive_modulo(data: list[int], shards: int) -> list[tuple[int, int]]:
    return [(i, i % shards) for i in data]


def jumping_hashing(data: list[int], shards: int) -> list[tuple[int, int]]:
    return [(i, jump.hash(i, shards)) for i in data]


def fibonacci_hash(i: int, shards: int):
    return (i * int(2654435769)) >> (32 - int(math.log2(shards)))


def fibonacci_hash_integer(x: int, M: int, w=32):
    A = (5**0.5 - 1) / 2
    K = int(A * (1 << w))  # Scale A to an integer constant
    hashed_value = (x * K) % (1 << w)
    return hashed_value % M


def fibonacci_hashing(data: list[int], shards: int) -> list[tuple[int, int]]:
    return [(i, fibonacci_hash_integer(i, shards)) for i in data]


class ConsistentHashRing:
    def __init__(self, nodes=None, replicas=100):
        self.replicas = replicas  # Number of virtual nodes per bucket
        self.ring = dict()
        self._sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_bucket(node)

    def _hash(self, key):
        h = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(h, 16)

    def add_bucket(self, node):
        for i in range(self.replicas):
            virtual_node_key = f"{node}:{i}"
            hash_value = self._hash(virtual_node_key)
            self.ring[hash_value] = node
            bisect.insort(self._sorted_keys, hash_value)

    def remove_bucket(self, node):
        for i in range(self.replicas):
            virtual_node_key = f"{node}:{i}"
            hash_value = self._hash(virtual_node_key)
            del self.ring[hash_value]
            index = bisect.bisect_left(self._sorted_keys, hash_value)
            del self._sorted_keys[index]

    def get_bucket(self, key):
        if not self.ring:
            return None
        hash_value = self._hash(key)
        index = bisect.bisect_right(self._sorted_keys, hash_value)
        if index == len(self._sorted_keys):
            index = 0
        return self.ring[self._sorted_keys[index]]


def consistent_hashing(data: list[int], shards: int, replicas) -> list[tuple[int, int]]:
    ring = ConsistentHashRing(range(shards), replicas=replicas)
    return [(i, int(ring.get_bucket(f"item-{i}"))) for i in data]


def hash_to_unit_interval(s: str) -> float:
    """Hashes a string onto the unit interval (0, 1]"""
    return (mmh3.hash128(s) + 1) / 2**128


@dataclass
class Node:
    """Class representing a node that is assigned keys as part of a weighted rendezvous hash."""

    name: str
    weight: float

    def compute_weighted_score(self, key: str):
        score = hash_to_unit_interval(f"{self.name}: {key}")
        log_score = 1.0 / -math.log(score)
        return self.weight * log_score


def determine_responsible_node(nodes: list[Node], key: str):
    """Determines which node of a set of nodes of various weights is responsible for the provided key."""
    return max(nodes, key=lambda node: node.compute_weighted_score(key), default=None)


def rendezvous_hashing(data: list[int], shards: int) -> list[tuple[int, int]]:
    nodes_map = {f"node-{i}": (i, Node(f"node-{i}", 100)) for i in range(shards)}
    nodes = [n for _, n in nodes_map.values()]
    return [
        (i, nodes_map[determine_responsible_node(nodes, f"item-{i}").name][0])
        for i in data
    ]


def compare_with_time(title, func, shards_start=20, shards_end=21):
    start_time = datetime.now()
    before = func(shards_start)
    after = func(shards_end)
    stop_time = datetime.now()
    elapsed_time = (stop_time - start_time).total_seconds()
    result = {"Time (sec)": elapsed_time}
    result.update(compare_shards(title, before, after))
    return result


def main():
    data = [hash(f"item-{i}") for i in range(1000000)]
    table = [
        compare_with_time("Naive modulo", lambda a: naive_modulo(data, a)),
        compare_with_time(
            "Jump consistent hashing", lambda a: jumping_hashing(data, a)
        ),
        compare_with_time("Fibonacci hashing", lambda a: fibonacci_hashing(data, a)),
        compare_with_time(
            "Consistent hashing (1 replica)", lambda a: consistent_hashing(data, a, 1)
        ),
        compare_with_time(
            "Consistent hashing (100 replicas)",
            lambda a: consistent_hashing(data, a, 100),
        ),
        compare_with_time(
            "Consistent hashing (1000 replicas)",
            lambda a: consistent_hashing(data, a, 1000),
        ),
        compare_with_time("Rendezvous hashing", lambda a: rendezvous_hashing(data, a)),
    ]

    print(tabulate(table, headers="keys", tablefmt="github", floatfmt=".2f"))


if __name__ == "__main__":
    main()
