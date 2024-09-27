---
title: "Interview Question Disk Reads"
date: 2024-09-24T17:27:24-07:00
draft: true
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
1. suggest to use a random or p2c cache eviction policy since they have quite close performance in real life applications.

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
There are data structures from the earlier era of computers optimized for utilizing disk cache more efficiently. 
Those structures may require the load profile to have certain properties like uneven look up frequency for different words
so more frequent words can be cached. This sometimes can fully replace other types of cache. 


