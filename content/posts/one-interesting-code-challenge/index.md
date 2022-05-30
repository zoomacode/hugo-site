---
title: "One Interesting Code Challenge"
date: 2022-05-29T11:22:58-07:00
draft: true
author: Anton Golubtsov
---

In my coding interviews I often use a simplified version of [this challenge from leetcode](https://leetcode.com/problems/find-all-anagrams-in-a-string/).
The simplified version I use: _Given two strings `s` and `p`, return true if `s` contains an anagram for `p`_.
I like this task because it can be solved in many, sometime unexpected, ways and it allows to ask
a lot of follow up question about the decisions a candidate made. Here I want to walk you through
the common and not so common solutions.

## The most expensive one

The first solutions that suggests the question itself is that: let's build a list of possible
anagrams and then we just need to check if the one of them is in the `s` string. That sounds simple,
right? There are a few problems with this approach. First of all, implementing an efficient algorithm
for generating all possible permutations is already quite a challenge. And secondly, the time complexity
for the final solution will be something like `O(s*p!)`. The factorial grows really fast `3! == 6`,
`5! == 120`, `10! == 3,628,800` and you don't want to deal with it.

## First step in the right direction

The first step toward more optimal solution is to tweak how we perceive the question just a little bit. In steads of
_return true if `s` contains an anagram for `p`_ we will use _return true if `s` contains a substring with character from string `p` in any order_.

## Sort

The order is a flexible thing. We can try to ignore or we can make things ordered in the way we want.
We can sort characters in `p` and then sort all possible substrings of length `p` in `s`.

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

It works but it is too slow. The time complexity for this approach is `O(s*p*log(p))`. In Leetcode, it fails because it times out in one of the test cases.

## Count

Ok. The sorting strings was not the best idea but it is another step in the right direction.
Imagine we have `p = "appleappleapple"` after sorting we will have `p = "aaaeeelllpppppp`
now we see that we care need to make sure that a `s`'s substring and `p` both have equal number of
the same characters. You may get to this point right away but not everybody as smart as you.
I'm definitely not of those people. Back to the business, we need to count number of characters in
a substring and in `p` and compare those numbers and Python has a nice little helper for us - `Counter`.

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

The main problem with the previous approach that we are rebuilding the counter on very iteration.
If we look at the substring as at a sliding window, we will see that we can reuse most of the counter's
content. We just need to add one character at the front and remove one at the back of the window.

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

We made it through but 23th percentile is not a big deal. Let's try to make it a little bit faster.

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

`timeit` measures how many seconds are needed to run an operation of a number of times. `timeit` runs one million iterations by default. `s.findAnagrams("abcabc","abc")` runs:

-   1 time, 1.42s or 12% of the time, construct the counter
-   6 times, 0.919s\*4 or 32.7% of the time, `cur.subtract(prev)`
-   6 times, 0.736s\*4 or 26.2% of the time, `cur.update(s[i])`
-   6 times, 0.08s\*4 or 2.8% of the time, `cur.get(prev)`
-   6 times, 0.09s\*4 or 3.2% of the time, `cur == p_counter`
-   4 times, 0.073s\*4 or 2.5% of the time, `list.append()`

The counter its ~60% of the execution time. The has one important constrain _s and p consist of lowercase English letters_.
That means that we can use a list for counting because there only 26 letter in English and all their codes a sequential. See: [ascii](https://en.wikipedia.org/wiki/ASCII).

Simple measurements shows that `list` can be 10x faster that `Counter`.

```python
>>> timeit('l[10]+=1', setup="l = [0]*26", globals=globals())
0.0989342509983544
>>> timeit('l1==l2', setup="l1 = [0]*26; l2=[0]*26", globals=globals())
0.08017934499912371
```

After tweaking our implementation we have something like this:

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

> Success
> Runtime: 133 ms, faster than 79.65% of Python3 online submissions for Find All Anagrams in a String.
> Memory Usage: 15.3 MB, less than 33.09% of Python3 online submissions for Find All Anagrams in a String.

We reduced the execution time by 65%.

```python
>>> timeit('s.findAnagrams("abcabc","abc")', globals=globals())
3.9490315559996816
```

Almost 80th percentile and 65% time reduction, that is not bad for a small change. The execution time actually fluctuates between 87ms and 165ms (p99 and p65). Here is a list of measurements: 87, 108, 115, 140, 145, 157, 165, 169 averaging at 135ms (p80).

## Removing the comparison and reaching O(s)

We reached 80th percentile but the algorithm remains `O(s*p)`. In this section we will remove `p` from `O(s*p)`. Removing `p` means that we need to identify that we found an anagram with constant time `O(1)`.
Here:

```python
            cur[prev - a] -= 1
            cur[c - a] += 1
```

We update just two integers and if we can look at those integers and tell whether or not they are equal to the numbers in `p_counter`. If we also can find a way to check that other numbers are also equal then we can immediately tell that we found an anagram.

We will start from subtracting `cur` from `p_counter` when they are equal, the results is a list of zeros. The first tweak is to remove `p_counter` and initialize `cur` by the negative numbers of characters.

```python
        cur = [0]*26
        for c in p:
            cur[c - a] -= 1
```

Now we can compare `cur` against a list of zeros. The next tweak is to know how many zeros `cur` already have so we can eliminate the list of zeros.

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

> Success
> Runtime: 99 ms, faster than 98.23% of Python3 online submissions for Find All Anagrams in a String.
> Memory Usage: 15.3 MB, less than 32.70% of Python3 online submissions for Find All Anagrams in a String.

But I wouldn't be so happy. The results in Leetcode fluctuate from p55 to p99 from run to run. Here is a list of measurements: 95,110, 112, 117, 131, 131, 135, 135,136,149,155,172,185,186 averaging at 139ms (p75).

## Making results more stable

We need more reliable environment to measure performance of the code. I took the tests sample which caused timeout in the very first version and will use it to measure performance. The performance test sources code: [perf_test.py](perf_test.py) and [perf_input.txt](perf_input.txt)

The results are pretty stable:

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

Now when we are the point when we operate at milliseconds level we can start optimizing small operations like `prev - a`. If we create a list of counter where first N elements we added just to remove ` - a` part from `cur[prev - a]`. We will win another 12% which brings us to 0.0089ms instead of 12.9256. That is 1452x faster.

```bash
SolutionSort:      12.9256 sec
SolutionCount:     7.9425 sec (-38.55% improvement)
SolutionFastCount: 0.0294 sec (-99.63% improvement)
SolutionList:      0.0120 sec (-59.20% improvement)
SolutionOs:        0.0101 sec (-15.66% improvement)
SolutionOs2:       0.0089 sec (-12.31% improvement)
```

## Making things even faster

There is at least one more trick. One of the recent candidate suggested an approach when we don't need to count characters at all. The candidate suggested to use character order agnostic hash function so instead of counting we will compute hash values for a substring and `p` and then just compare two numbers.

However, there is one flow as length of `p` grows, the hash grows as well. In languages like C++ it will lead to overflowing the integer.
But in Python it leads to more and more expensive arithmetic and as result Leetcode test fails even earlier that the first version.

```bash
>>> timeit('50357543 * 9')
0.013241855999996943
>>> timeit('6634282395641056463368422676523964230824061054656696147421638381867962461616370766912810646544439112552112104094315979216387096611584409353999775 * 9')
0.09212760000002618
```

Anyhow, here are performance test results:

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
