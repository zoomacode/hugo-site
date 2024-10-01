---
title: "Data Sharding(Partitioning) Algorithms"
date: 2024-09-30T17:20:24-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
    - Sharding
---

I used to work close with incredibly smart people who was dealing with things like data sharding on daily basis from them I learned a lot on that topic. Later I moved to a different role where that knowledge was not needed and faded away over the time. Here I'm trying to reclaim to myself that long forgotten knowledge.

### Intro

Sharding is a process of assigning an item to a shard - a smaller chunk of data out of a large database or other service. The general idea is that we can distribute data or service across multiple locations
and handle large volumes of data or handle more requests and with replication we can scale even more and make the system more resilient etc. But we need to have clear rules on how we assign partitions aka shards so
that we can route requests to the right location.

The easiest way to do that is to take a reminder of an item id (or item hash) and use it as a shard id:

```
shard = item.id mod M
```

where `M` is a total number of shards. However, it has a drawback that any change in the total number of shards leads to moving all items to new shards. This maybe ok for some cases like offline data processing but
for cases like sharding a database it means that you need to move all data from one server to some different server. When we increase the number of shards from 20 to 21, ~95% of the items has to be moved.

```
affected_items_pct = shards_before / shards_after * 100
```

### Replication

Most of the algorithms can be modified to support replication by for example introducing multiple copies of an object for example by adding a replica id suffix and the same works for multiple service nodes.

### Consistent hashing

The idea of consistent hashing is pretty simple let's take all possible hash values of nodes and items
put on a single line where 0 is on the left, infinity is on the right. And then we will assign an item to a node/shard/partition on the right of the item. Basically an item assigned to the first shard which `hash(shard) > hash(item)`. But it will create a problem for the items on the right side of all shards so we will just use
the first shard from the left for those items. On the most website it is described as a circle but I prefer a line. It just makes more sense to me.

Because of this setup consistent when we add a new node only a fraction of items needs to be moved to a new location. In practice to make the process even less disrupting, people usually introduce a several copies
of a node with different hashes like `hash("node-1-1")`, `hash("node-1-2")`, ... , `hash("node-1-20")`. This creates a set of evenly distributed shards on the line/circle and each of them accepts only a fraction
of changes in case of repartitioning.

On the negative side: you need to know shard hashes in order to identify a shard and in addition
each shard needs to be presented around 1000 times in order to get even distribution of items per shard.

See: [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm) and [original paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)

### Jump Consistent Hashing

Jump Consistent Hashing uses some mathematical magic[^1] to "jump" through a buckets (shards) until suddenly
it jumps out of all buckets.

```cpp
int32_t JumpConsistentHash(uint64_t key, int32_t num_buckets) {
    int64_t b = ­1, j = 0;

    while (j < num_buckets) {
        b=j;
        key = key * 2862933555777941757ULL + 1;
        j = (b + 1) * (double(1LL << 31) / double((key >> 33) + 1));
    }

    return b;
}
```

It has three main advantages:

1. it does not require to know shard hashes on every "load balancing" machine;
1. it does not require to create a 1000 of virtual nodes to guarantee even distribution of items.
1. it is faster.

And as other algorithms can be combined with replication by introducing virtual items.

See: [A Fast, Minimal Memory, Consistent Hash Algorithm](https://arxiv.org/pdf/1406.2294)

### Fibonacci Hashing

There is a nice an interesting alternative to modulo hashing called Fibonacci hashing. I highly recommend to explore it, check out the footnotes, it uses the fibonacci numbers for assigning shards but I couldn't make it work with dynamic number of clusters outside of the consistent hashing.

See: [Fibonacci Hashing: The Optimization that the World Forgot (or: a Better Alternative to Integer Modulo)](https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/)

### Rendezvous Hashing

Rendezvous is an interesting one. You need to take a shard key and an item key and hash them together, do it for each node and then pick the maximum hash across all other hashes. It words surprisingly well and is used in big corporations.

The main drawbacks:

1. you need to know node keys
2. in naive implementation works in O(n) time in less naive implementation works in O(log n).

See: [Rendezvous Hashing](https://en.wikipedia.org/wiki/Rendezvous_hashing)

### Test

To show how different strategies perform I've wrote a short [test](./shards.py). It tests 2 things: evenness of data distribution across shards (standard deviation) and stability of assigned shards as the number of shards grows from 20 to 21 in our cases. I've also included elapsed time for a reference.

| Time (sec) | Title                              | Overlap | Shards (before) | Shards (after) | Items per shard | Items per shard (std) |
| ---------- | ---------------------------------- | ------- | --------------- | -------------- | --------------- | --------------------- |
| 0.19       | Naive modulo                       | 4.77    | 20              | 21             | 47619.05        | 156.67                |
| 0.32       | Jump consistent hashing            | 95.24   | 20              | 21             | 47619.05        | 237.10                |
| 0.80       | Fibonacci hashing                  | 4.80    | 20              | 21             | 47619.05        | 222.53                |
| 2.15       | Consistent hashing (1 replica)     | 93.71   | 20              | 21             | 47619.05        | 39882.89              |
| 2.47       | Consistent hashing (100 replicas)  | 94.68   | 20              | 21             | 47619.05        | 6105.93               |
| 2.81       | Consistent hashing (1000 replicas) | 95.25   | 20              | 21             | 47619.05        | 1227.54               |
| 29.55      | Rendezvous hashing                 | 95.28   | 20              | 21             | 47619.05        | 218.09                |

As we can see consistent hashing indeed gives least even data distribution but it keeps assigned shards relatively stable. I hope it will help someone to decided what is best for their use-case. For me, it was an exercise in brushing up the forgotten knowledge.

### References

1. [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm)
1. [A Fast, Minimal Memory, Consistent Hash Algorithm](https://arxiv.org/pdf/1406.2294)
1. [Consistent hashing and random trees: Distributed caching protocols for relieving hot spots on the World Wide Web](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)
1. [Fibonacci Hashing: The Optimization that the World Forgot (or: a Better Alternative to Integer Modulo)](https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/)
1. [Fibonacci Hashing from Data Structures and Algorithms with Object-Oriented Design Patterns in C++ by Bruno R. Preiss](https://book.huihoo.com/data-structures-and-algorithms-with-object-oriented-design-patterns-in-c++/html/page214.html)
1. [Scrambling Eggs for Spotify with Knuth's Fibonacci Hashing](https://pncnmnp.github.io/blogs/fibonacci-hashing.html)
1. [Rendezvous Hashing](https://en.wikipedia.org/wiki/Rendezvous_hashing)

[^1]: [Consistent hashing algorithm](https://highscalability.com/consistent-hashing-algorithm)
