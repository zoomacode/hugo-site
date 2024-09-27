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
Even though it is mentioned in the task, people often ignore streaming. I've asked a few candidates how they would implement the concept of streams and lazy evaluation in their language anf often the candidates 
