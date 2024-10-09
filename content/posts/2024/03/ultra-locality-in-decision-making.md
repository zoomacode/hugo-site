---
title: "Ultra-locality in Decision Making and Free Will"
date: 2024-03-23T21:15:45-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - random
---

This time we explore the wonderful world of ultra-locality in decision-making and its connection to free will, good, evil, and God.

### Part One: Ultra-locality and Free Will

The same [Joscha Bach: Life, Intelligence, Consciousness, AI & the Future of Humans | Lex Fridman Podcast #392](https://www.youtube.com/watch?v=e8qJsk1j2zE) podcast I mentioned in the previous post [AI, people, trees, and mushrooms: the same software different hardware](https://antongolubtsov.substack.com/p/ai-people-trees-and-mushrooms-the) triggered another chain of thought. Joscha was talking about how our neurons always operate using data available right here and right now. That is enough to build complex systems like the human brain. Working together, neurons form parts responsible for memories, image processing, data buses, etc. But ultimately, each of them individually works only with data provided by other neurons. In a similar fashion, neural networks in GPTs are just a multiplication of matrices connected with each other, forming memories, attention, generation, etc.

I love to think of people, neurons, cells, viruses as agents of free will, each acting based on available information and in a way that benefits them long-term or short-term. God, with all good and bad, joy and suffering, perfectly fits into the question since he does not interfere with free will. Hence, whatever happens to us is a result of our own actions or actions of other free will agents.

There are a few ways to reduce the impact from bad acting agents: eliminate those, reduce the probability of encountering them, and improve our resilience. The first part looks improbable, the second one can be achieved in various ways like better hygiene, a nice neighborhood, better education, etc. However, if we focus only on the first two, we can be completely unprepared for encountering bad actors. Even small issues like a cold, peanut butter, or dust can knock us out.

We got a little sidetracked here. Let's have a look at some real-life examples of ultra-locality and globalization.

### Part Two: Ultra-locality vs. Globalization in Real Life

Each of us, to an extent, also works in ultra-locality mode; we make decisions based on the information we have. But at this level, we start shifting our focus towards global, centralized decision-making instead of federation. When we decide to collect more data, consult with an expert, or form a committee, we are switching from local, instantaneous decisions to globally optimized, delayed decisions. Both modes have pros and cons, but the delayed, global mode seems harder to control and optimize.

There are cases where global alignment is required, like food safety standards, air traffic control protocols, communication standards, etc. However, in many cases, global optimization introduces more control, less freedom, and more rigid, harder-to-maintain structures. For example, a strong federal government and weak local government lead to large delays in addressing local problems just because the communication cycle from people to the government and back is much longer than in the case of a strong local government, like a city government, where the communication loop is shorter. Also, higher-level governments have limited visibility on local problems, so I would expect them to solve problems instead of making things worse.

There are a few interesting cases of ultra-locality and globalization in tech. The first example that comes to mind is load balancing requests coming to a website or service. We want to distribute the traffic in a way that each server is equally utilized, and there is no imbalance in the system. One approach is to have a global supervisor that knows the load of each individual server and then decides to pick the least loaded one. Similarly, the implementation of the least recently used (LRU) caching to minimize load on the server side requires a global overview of what was used and when.

In both cases, the natural and naïve response is always to pick the best option, which can be problematic to implement. Instead, we may want to utilize an ultra-local decision-making process called "the power of two choices." In that approach, we randomly pick two or more candidates and select the best one out of those two. It may seem suboptimal for a single decision, but when we have thousands and millions of such decisions, they all converge to the global optimum[^1]. See other links in the footnotes.

Another algorithm that comes to mind is [BBR: Congestion-Based Congestion Control - ACM Queue](https://queue.acm.org/detail.cfm?id=3022184)[^4] from Google, a low-level algorithm that works on network devices like switches and prevents data congestion. It replaced the previous generation of congestion control algorithms in and between Google data centers in 2016. The key difference is that the new algorithm is proactive. The algorithm measures effective network bandwidth to any destination by observing network packages coming through it and nothing else.

The last and most interesting example of ultra-locality is a probabilistic algorithm for building multi-dimensional skip lists[^5]. The problem skip lists help to solve is the search for K nearest neighbors in multi-dimensional space. It is needed to find semantically related search results that do not have the same words as the user request. A balanced, efficient skip list can be built relatively easily. However, it is hard to keep that globally balanced and efficient. Instead, people use a probabilistic version of a skip list where global optimization is replaced by a series of random decisions to select a position to add a new item to the skip list. And again, similarly to the load balancing problem, small local decisions lead to the global optimum.

### Conclusion

There is a tendency to give the power to make decisions that affect us all to some supervisor whom we believe will make that decision for us, and it will be better than we could decide for ourselves. However, there are plenty of examples where ultra-locality provides similar or better results with no globalization overhead.

_Originally posted on Substack:_ https://antongolubtsov.substack.com/p/ultra-locality-in-decision-making

---

**_Footnotes_**:
[^1]: [The Power of Two Random Choices: A Survey of Techniques and Results](https://danluu.com/2choices-eviction/)
[^2]: [Caches: LRU v. random](https://danluu.com/2choices-eviction/)
[^3]: [Supported load balancers — envoy 1.30.0-dev-b68af0 documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-least-request)
[^4]: [BBR: Congestion-Based Congestion Control - ACM Queue](https://queue.acm.org/detail.cfm?id=3022184)
[^5]: [Skip List Data Structures for Multidimensional Data](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=3323f942f3dd67bd4d27cc54349f07397452c84f)
