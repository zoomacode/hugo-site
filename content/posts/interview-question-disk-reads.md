---
title: "An Interview Question: Optimization of Disk Read costs"
date: 2024-09-24T17:27:24-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Interview
    - Software Development
    - Code Challenges
---

One of the questions are really love asking during coding interviews is this:

---

_Given a continuous stream of words, a dictionary on disk and cost associated to read from disk, create a stream processor that returns true when a word exists in the dictionary while minimizing the cost of reading from disk.
Example:_

```
Dictionary: {Dog, Cat, Bird, Lion, ...}
Input: [Dog, Cat, Aghd, ...]
Output: [True, True, False, ...]
```

_The output is true, true, false because dog and cat exist in the dictionary of words while Aghd is not considered a word._

---

The main reason is that the question allows to evolve the conversation in multiple ways covering a wide range of topics from simple memoization to more complex like data structures on disk optimized for reads, and disk caching.

**Level 1: memorization**
Memoization is one of the most frequent responses and in many cases people suggest LRU cache as a way to implement memorization. There are a few things the candidate can do to stand out:

1. instead of implementing an LRU cache, which simple but annoyingly wordy with bunch of corner case if you want to implement everything including linked lists, the candidate can just suggest using the standard libraries, for example Python has built-in LRU cache as a decorator.
1. suggest to use a random or p2c cache eviction policy since they have quite close performance in real life applications. See: [comparison of cache eviction policies](./cache-eviction-lru-and-p2c/)

**Level 2: streaming**
Even though it is mentioned in the task, people often ignore streaming. I've asked a few candidates how they would implement the concept of streams and lazy evaluation in their language and often the candidates couldn't answer.
Knowing how, why, and why use streaming can be a requirement for certain roles.

**Level 3: data storage optimization**
The dictionary can be stored in many different ways some of them are more disk search friendlier than others. The options the candidate can explore are quite broad:

1. a sorted file;
1. a trie on disk optimized for fast look ups;
1. an local database like sqlite3 or where and be run inside of an application or as a sidecar.
1. something else like building a trie by creating a millions of folders and subfolders.

The candidate rarely considers anything besides the first option if any.

**Level 4: disk cache and memmap**
There are data structures, sometimes from the earlier era of computers, optimized for utilizing disk cache more efficiently.
Those structures may require a specific query distribution profile to make it work. But when it works the dick cache can cover fully replace manually implement regular cache.

This is particularly interesting part since it can be an indication that the candidate have very peculiar experience very few people had. For example, I wouldn't be able to bring it up if I'd worked for a company which actually uses at scale.

**Level 5: challenging the problem statement**
In some cases, yes/no questions may have looser constrains. For example, it could be ok have false positive answers but false negatives can be completely unacceptable in that case we can use Bloom filters.

For example, we know that let's say 50% of requests will give `False`. In that case we can use a Bloom filter to drop those hard nos. And then we use an LRU cache for the rest of the traffic making the cache 2x more efficient.

Another way to use bloom filters for caching: https://en.wikipedia.org/wiki/Bloom_filter#Cache_filtering the whole page is quite interesting reading.
