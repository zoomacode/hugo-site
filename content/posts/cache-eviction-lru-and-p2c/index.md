---
title: "Cache eviction policies: LRU vs random vs p2c"
date: 2024-08-25T11:22:58-07:00
draft: True
author: Anton Golubtsov
toc: true
---

Every so often I'm search the internet in attempt to find a article which will compare least recently used (LRU), random, and power of two choices (p2c) cache eviction policies and every time I can not find a article that will answer all my question or provide illustrations I looked for.
So it time to write something myself I suppose.

We will be exploring how those policies perform for a simple HTTP server.
We will explore the following cases:

1. cache hit rate for queries of equal importance
2. time saved by each strategy
3. and we will try to optimize one of the strategies to reduce total wait time even further

### Setup

Our server will be a python function which will be called with different parameters. We will cache calls that function using different strategies and cached sizes.

In the next, step we will try to make it a little bit close to the real-life, still far but close.
So here we will introduce query latency and see if the results we are any different.

We will use a gamma distribution to mimic "latency" since HTTP requests latency usually follow it.

### A simple cache hit

To make our "requests" look more like a real traffic we will make some of them more frequent than others.
Depends on the service the query frequency imbalance can be more or less prominent.
In companies I worked for the request imbalance was a very standard situation.

If your service all requests are equally probable then the cache hit rate is equal to the fraction of unique
requests it can fit in. For example, if the cache fits 20% of unique requests, then the hit rate is close to 20% as well.

Using the following code: [link](./cache-experiments-naive.py),
we generated a set of 100,000 unique requests, and a set of request of 1,000,000 requests using gamma distribution to generate weights or frequencies.
Then we tried different cache eviction policies strategies, and different cache sizes.

From this experiment we can see that all four strategies, we added a power of 3 choices just for fun, are close to each other. That makes the idea of implementing an LRU cache cache instead of a simple power of N choices less appealing since p2c is much easier to implement from scratch.

On the other hand there is plenty of LRU implementations so you can pick whatever you like. Who cares? Except probably an interviewer in your job interview.
![](./images/query-weights-distribution-naive.png)
![](./images/query-ids-distribution-naive.png)
![](./images/cache-eviction-lru-and-p2c-naive.png)

| Cache Size | Random | LRU    | P2C    | P3C    |
| ---------- | ------ | ------ | ------ | ------ |
| 1          | 3.906  | 3.97   | 4.071  | 4.166  |
| 2          | 6.922  | 7.106  | 7.215  | 7.31   |
| 3          | 9.431  | 9.354  | 10.009 | 10.1   |
| -          | -      | -      | -      | -      |
| 19         | 37.828 | 36.678 | 38.235 | 38.867 |
| 20         | 39.639 | 39.359 | 39.984 | 40.137 |

### Latency savings

Let's introduce latency into the system and try to see how much of it can be saved by applying all the caching strategies with no change to them.

### Conclusion
