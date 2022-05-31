---
title: "One Interesting Code Challenge from Leetcode: finding anagrams in a string"
date: 2022-05-29T11:22:58-07:00
draft: true
author: Anton Golubtsov
---

In my coding interviews I often use a simplified version of [this challenge from Leetcode](https://Leetcode.com/problems/find-all-anagrams-in-a-string/).
The simplified version I use: _Given two strings `s` and `p`, return true if `s` contains an anagram for `p`_.
I like this task because the solution and be improved little by little and there are a lot things to discuss. From algorithmic complexity to CPU cache level optimization. Here I want to walk you through how I solved that challenge for the first time.

## The most expensive solution

The first solutions that is suggested by the question is that: let's build a list of possible
anagrams and then we just check if the one of them is in the `s` string. Sounds simple,
right? There are a few problems with this approach. First of all, implementing an efficient algorithm
for generating all possible permutations is already quite a challenge. And secondly, the time complexity
for the final solution will be something like `O(s*p!)`. The factorial grows really fast `3! == 6`,
`5! == 120`, `10! == 3,628,800` and you don't want to deal with it.

## First step in the right direction

The first step towards a more optimal solution is to tweak a little bit the way how we perceive the question just. Instead
_return true if `s` contains an anagram for `p`_ we will use _return true if `s` contains a substring with character from string `p` in any order_. This will change the way how we think about the problem and unlock more solutions.

## Sort

One of the ways to work with unordered data is make it ordered in the way we want.
So we sort characters in `p` and then sort all possible substrings of length `p` in `s`.

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) <1 or len(p)<1:
            return result

        p_len = len(p)
        p_sorted = sorted(p)
        for i in range(len(s)-p_len+1):
            cur = sorted(s[i:i+p_len])
            if cur == p_sorted:
                result.append(i)

        return result
```

> 34 / 61 test cases passed.

It works but it is too slow and it timed out at one of the test cases when I submitted it to Leetcode. The time complexity for this approach is `O(s*p*log(p))`.

## Count

Ok. The sorting strings was not the best idea but we can learn something from it. Imagine that we have `p = "appleappleapple"` after the sorting we have `p = "aaaeeelllpppppp"`.
We can present that string as a dict `{ 'a': 3, 'e':3, 'l':3, 'p':6 }`. We can present any string in a similar way. Building the dictionary is a simpler operation that sorting. So we can count number of characters in
a substring and in `p` and then compare those numbers. Python has a nice little helper to simplify that task - `collections.Counter`.

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) <1 or len(p)<1:
            return result

        p_len = len(p)
        p_counter = Counter([s for s in p])
        cur = Counter([ss for ss in s[:p_len]])
        for i in range(len(s)-p_len+1):
            cur = Counter([ss for ss in s[i:i+p_len]])
            if cur == p_counter:
                result.append(i)

        return result
```

> 61 / 61 test cases passed, but took too long.

Ok. We again "Exceeded the time" but this time it was overall time for all 61 tests. Our solution has
`O(s*p)` complexity which is of corse better than `O(s*p*log(p))` but still not `O(s)`.

## Counting but faster

The main problem with the previous approach is that we are rebuilding the counter on very iteration.
We look at the substring as at a sliding window so we need to add one character at the front and remove one at the back of the window.
That will allow us to keep the counter between iterations.

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        result = []
        if len(s) < len(p) or len(s) <1 or len(p)<1:
            return result

        p_len = len(p)
        p_counter = Counter([s for s in p])
        cur = Counter([ss for ss in s[:p_len]])
        i = p_len-1
        for i in range(len(p), len(s)):
            if cur == p_counter:
                result.append(i-p_len)

            prev = s[i-p_len]
            cur.subtract(prev)
            cur.update(s[i])

            if not cur.get(prev):
                cur.pop(prev)

        if cur == p_counter:
            result.append(i-p_len+1)

        return result
```

> Success  
> Runtime: 426 ms, faster than 23.71% of Python3 online submissions for Find All Anagrams in a String.  
> Memory Usage: 15.2 MB, less than 33.09% of Python3 online submissions for Find All Anagrams in a String.

We finally made it through but 23th percentile is not a great result. Let's try to make it a little bit faster.

## Cutting costs: the counter

It may look that we reached `O(s)` time complexity and it can't be improved. But in fact, the complexity is still `O(s*p)` because of `cur == p_counter`. However a largest problem is that updating the counter is an expensive operation. To confirm it we can do simple measurements:

```
>>> s = Solution()
>>> timeit('s.findAnagrams("abcabc","abc")', globals=globals())
11.242373244000191
>>> timeit('Counter("abc")', setup="", globals=globals())
1.417118921999645
>>> timeit('ll.append("a")', setup="ll = []", globals=globals())
0.07390610099992045
>>> c = Counter("abc")
>>> timeit('c.update("a")', globals=globals())
0.7364297260000967
>>> timeit('c.subtract("a")', globals=globals())
0.9186600939992786
>>> timeit('ca == cb', globals=globals())
0.09419484599857242
>>> timeit('ca.get("a")', globals=globals())
0.08134488799987594
```

`timeit` measures how many seconds are needed to run an operation for a number of times. `timeit` runs one million iterations by default. `s.findAnagrams("abcabc","abc")` runs:

-   1 time, 1.42s or 12% of the time, construct the counter
-   6 times, 0.919s\*4 or 32.7% of the time, `cur.subtract(prev)`
-   6 times, 0.736s\*4 or 26.2% of the time, `cur.update(s[i])`
-   6 times, 0.08s\*4 or 2.8% of the time, `cur.get(prev)`
-   6 times, 0.09s\*4 or 3.2% of the time, `cur == p_counter`
-   4 times, 0.073s\*4 or 2.5% of the time, `list.append()`

The counter consumes ~60% of the execution time. But do we really need the full-fledged generic Counter or we can use something simpler and faster. The task has one important constrain _s and p consist of lowercase English letters_.
That means that we can use a list of 26 elements, one per each English letter. Thank to the [ascii](https://en.wikipedia.org/wiki/ASCII) standard the codes of those letters are sequential so we don't need a dictionary from translation of a single letter to its counter.

I measured `list` performance using `timeit` to confirm that `list` faster that `dict`.

```python
>>> timeit('l[10]+=1', setup="l = [0]*26", globals=globals())
0.0989342509983544
>>> timeit('l1==l2', setup="l1 = [0]*26; l2=[0]*26", globals=globals())
0.08017934499912371
```

After replacing `Counter` by `list` the implementation looks like like this:

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        result = []
        if len(s) < len(p) or len(s) <1 or len(p)<1:
            return result
        p_len = len(p)
        a = ord('a')

        p_counter = [0]*26
        for c in p:
            p_counter[c - a] += 1

        cur = [0]*26
        for c in s[:p_len]:
            cur[c - a] += 1

        i = p_len-1
        for i in range(len(p), len(s)):
            if cur == p_counter:
                result.append(i-p_len)
            c = s[i]
            prev = s[i-p_len]
            cur[prev - a] -= 1
            cur[c - a] += 1
        if cur == p_counter:
            result.append(i-p_len+1)
        return result
```

The changed reduced the execution time by 65% (from 11.24s to 3.95s).

```python
>>> timeit('s.findAnagrams("abcabc","abc")', globals=globals())
3.9490315559996816
```

## Removing the comparison and reaching O(s)

We've improved the implementation but the algorithmic complexity remains the same -`O(s*p)`. In this section we will remove `p` from `O(s*p)` and reduce the costs even further. The `p` parts hides in `cur == p_counter`.

When `cur == p_counter` is true difference between `cur` and `p_counter` give a list of zeros. We can use it for our advantage. Since `p_counter` is a constant, `cur == p_counter` cn be replaced by `(cur - p_counter) == (p_counter - p_counter)` which can be replaced by `(cur - p_counter) == [0]*26`.

```python
        cur = [0]*26
        for c in p:
            cur[c - a] -= 1
```

Now the `[0]*26` part can be replaced by a counter that tracks number of zeros in `cur`. We can implement a zeros' tracker by incrementing a zero's counter by checking a letter counter value before updating it.

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        s = s.encode("ascii")
        p = p.encode("ascii")
        result = []
        if len(s) < len(p) or len(s) <1 or len(p)<1:
            return result
        p_len = len(p)
        a = ord('a')
        cur = [0]*26

        for c in s[:p_len]:
            cur[c - a] += 1
        for c in p:
            cur[c - a] -= 1

        zeros = len([0 for i in cur if i == 0])
        i = p_len-1
        for i in range(len(p), len(s)):
            if zeros == 26:
                result.append(i-p_len)
            c = s[i]
            prev = s[i-p_len]

            p_cur = cur[prev - a]
            zeros += 1 if p_cur == 1 else 0
            zeros += -1 if p_cur == 0 else 0
            cur[prev - a] -= 1

            c_cur = cur[c - a]
            zeros += 1 if c_cur == -1 else 0
            zeros += -1 if c_cur == 0 else 0
            cur[c - a] += 1
        if zeros == 26:
            result.append(i-p_len+1)
        return result
```

And again a performance test:

```python
>>> timeit('s.findAnagrams("abcabc","abc")', globals=globals())
6.378495043000001
```

It looks like we make things worse. However, it is not entirely true, the new initialization logic is heavier that the old one and we used a simple test case. Let's try something less simple.

## Performance tests

To make tests more reliable I wrote a small script and put one of the toughest test cases from [Leetcode](https://Leetcode.com) into a text file. As a tests sample I picked the one which caused timeout in the very first version. The performance test sources code: [perf_test.py](perf_test.py) and [perf_input.txt](perf_input.txt)

```bash
$ python3 content/posts/perf_test.py
SolutionSort:      12.7849 sec
SolutionCount:     7.9685 sec (-37.67% improvement)
SolutionFastCount: 0.0296 sec (-99.63% improvement)
SolutionList:      0.0119 sec (-59.82% improvement)
SolutionOs:        0.0101 sec (-15.24% improvement)
```

The final solution is 1200x faster than the initial one.

But we are not done here.

## One more teeny-tiny tweak

Now when we are the point when we operate at milliseconds level we can start optimizing small operations like `prev - a`. We can remove `- a` part by creating a counter list where we added padding N elements so `cur[prev]` operations hit a counter inside of the list. That small change won another 12%. That brings us to 0.0089ms instead of 12.9256 which is 1452x faster that the original version.

```bash
SolutionSort:      12.9256 sec
SolutionCount:     7.9425 sec (-38.55% improvement)
SolutionFastCount: 0.0294 sec (-99.63% improvement)
SolutionList:      0.0120 sec (-59.20% improvement)
SolutionOs:        0.0101 sec (-15.66% improvement)
SolutionOs2:       0.0089 sec (-12.31% improvement)
```

## A different approach: hashing

There is at least one more approach. A recent candidate I interviewed suggested an approach when we don't need to count characters at all. The candidate suggested to use character order agnostic hash function so instead of counting we will compute hash values for a substring and `p` and then just compare two numbers.

However, there is one flaw, at least in Python, as length of `p` grows, the hash grows as well and it leads to more expensive math operations.

```bash
>>> timeit('50357543 * 9')
0.013241855999996943
>>> timeit('6634282395641056463368422676523964230824061054656696147421638381867962461616370766912810646544439112552112104094315979216387096611584409353999775 * 9')
0.09212760000002618
```

[Leetcode](https://Leetcode.com) test fails even earlier that the first version. But here are performance test results anyway:

```bash
SolutionSort:      12.9363 sec
SolutionCount:     8.1108 sec (-37.30% improvement)
SolutionFastCount: 0.0293 sec (-99.64% improvement)
SolutionList:      0.0118 sec (-59.69% improvement)
SolutionOs:        0.0099 sec (-15.86% improvement)
SolutionOs2:       0.0089 sec (-10.81% improvement)
SolutionHash:      0.3288 sec (3607.15% degradation)
```

## Conclusion

There is not much to conclude really. I just wanted to show how I was solving the challenging step by step when I found it for the first time. And it was also interesting to observe how the performance improves from small changes while I was writing the post.
