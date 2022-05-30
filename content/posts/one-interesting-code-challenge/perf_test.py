#!/usr/bin/env python3
from collections import Counter
from timeit import timeit
from typing import List

with open("perf_input.txt") as fp:
    s = fp.readline().strip("\n")
    p = fp.readline().strip("\n")


class SolutionSort:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result

        p_len = len(p)
        p_sorted = sorted(p)
        for i in range(len(s) - p_len + 1):
            cur = sorted(s[i : i + p_len])
            if cur == p_sorted:
                result.append(i)

        return result


class SolutionCount:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result

        p_len = len(p)
        p_counter = Counter([s for s in p])
        cur = Counter([ss for ss in s[:p_len]])
        for i in range(len(s) - p_len + 1):
            cur = Counter([ss for ss in s[i : i + p_len]])
            if cur == p_counter:
                result.append(i)

        return result


class SolutionFastCount:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result

        p_len = len(p)
        p_counter = Counter([s for s in p])
        cur = Counter([ss for ss in s[:p_len]])
        i = p_len - 1
        for i in range(len(p), len(s)):
            if cur == p_counter:
                result.append(i - p_len)

            prev = s[i - p_len]
            cur.subtract(prev)
            cur.update(s[i])

            if not cur.get(prev):
                cur.pop(prev)

        if cur == p_counter:
            result.append(i - p_len + 1)

        return result


class SolutionList:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result
        p_len = len(p)
        a = ord("a")

        p_counter = [0] * 26
        for c in p:
            p_counter[c - a] += 1

        cur = [0] * 26
        for c in s[:p_len]:
            cur[c - a] += 1

        i = p_len - 1
        for i in range(len(p), len(s)):
            if cur == p_counter:
                result.append(i - p_len)
            c = s[i]
            prev = s[i - p_len]
            cur[prev - a] -= 1
            cur[c - a] += 1
        if cur == p_counter:
            result.append(i - p_len + 1)
        return result


class SolutionOs:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result
        p_len = len(p)
        a = ord("a")
        cur = [0] * 26

        for c in s[:p_len]:
            cur[c - a] += 1
        for c in p:
            cur[c - a] -= 1

        zeros = len([0 for i in cur if i == 0])
        i = p_len - 1
        for i in range(len(p), len(s)):
            if zeros == 26:
                result.append(i - p_len)
            c = s[i]
            prev = s[i - p_len]

            p_cur = cur[prev - a]
            zeros += 1 if p_cur == 1 else 0
            zeros += -1 if p_cur == 0 else 0
            cur[prev - a] -= 1

            c_cur = cur[c - a]
            zeros += 1 if c_cur == -1 else 0
            zeros += -1 if c_cur == 0 else 0
            cur[c - a] += 1
        if zeros == 26:
            result.append(i - p_len + 1)
        return result


class SolutionOs2:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result
        p_len = len(p)
        a = ord("a")
        counter_len = ord("z") + 1
        cur = [0] * counter_len

        for c in s[:p_len]:
            cur[c] += 1
        for c in p:
            cur[c] -= 1

        zeros = len([0 for i in cur if i == 0])
        i = p_len - 1
        for i in range(len(p), len(s)):
            if zeros == counter_len:
                result.append(i - p_len)
            c = s[i]
            prev = s[i - p_len]

            p_cur = cur[prev]
            zeros += 1 if p_cur == 1 else 0
            zeros += -1 if p_cur == 0 else 0
            cur[prev] -= 1

            c_cur = cur[c]
            zeros += 1 if c_cur == -1 else 0
            zeros += -1 if c_cur == 0 else 0
            cur[c] += 1
        if zeros == counter_len:
            result.append(i - p_len + 1)
        return result


class SolutionHash:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        primes = [0] * (ord("a")) + [
            2,
            3,
            5,
            7,
            11,
            13,
            17,
            19,
            23,
            29,
            31,
            37,
            41,
            43,
            47,
            53,
            59,
            61,
            67,
            71,
            73,
            79,
            83,
            89,
            97,
            101,
        ]

        result = []
        if len(s) < len(p) or len(s) < 1 or len(p) < 1:
            return result

        p_len = len(p)
        a = ord("a")

        p_hash = 1
        for c in p:
            p_hash *= primes[c]

        cur = 1
        for c in s[:p_len]:
            cur *= primes[c]

        i = p_len - 1
        for i in range(len(p), len(s)):
            if cur == p_hash:
                result.append(i - p_len)

            c = s[i]
            prev = s[i - p_len]

            cur *= primes[c]
            cur //= primes[prev]
        if cur == p_hash:
            result.append(i - p_len + 1)
        return result


number = 1

solution = SolutionSort()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionSort:      {t:.04f} sec")
t_prev = t

solution = SolutionCount()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionCount:     {t:.04f} sec ({(t/t_prev-1)*100:.02f}% improvement)")
t_prev = t

solution = SolutionFastCount()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionFastCount: {t:.04f} sec ({(t/t_prev-1)*100:.02f}% improvement)")
t_prev = t

solution = SolutionList()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionList:      {t:.04f} sec ({(t/t_prev-1)*100:.02f}% improvement)")
t_prev = t

solution = SolutionOs()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionOs:        {t:.04f} sec ({(t/t_prev-1)*100:.02f}% improvement)")
t_prev = t

solution = SolutionOs2()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionOs2:       {t:.04f} sec ({(t/t_prev-1)*100:.02f}% improvement)")
t_prev = t

solution = SolutionHash()
t = timeit("solution.findAnagrams(s,p)", globals=globals(), number=number)
print(f"SolutionHash:      {t:.04f} sec ({(t/t_prev-1)*100:.02f}% degradation)")
t_prev = t