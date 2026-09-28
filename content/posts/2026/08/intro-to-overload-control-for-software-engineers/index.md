---
title: "Intro to Overload Control for Software Engineers"
date: 2026-08-16T00:00:00-07:00
draft: true
author: Anton Golubtsov
summary: "Why one busy service collapses while another keeps working, and how to build the second kind."
toc: true
math: true
tags:
    - Software Development
    - Distributed Systems
    - Queueing Theory
---

A large part of my career has been spent working with systems that process a lot of user requests. I have seen some of them survive sustained traffic far above their capacity. Others fell apart at a load they should have been able to handle. The difference was rarely explained by the number of pods or the programming language.

Let me start with two systems.

### System A: total collapse

System A was a fairly standard request and response service running in Kubernetes. It received a request, did some work, called other services, and returned the result. Autoscaling added pods when load increased. This had worked well enough through ordinary peaks.

Then incoming traffic reached roughly five times the service's maximum capacity. Kubernetes scaled the deployment to its configured limit. CPU and memory were full, useful throughput fell close to zero, and new pods began restarting soon after they joined the serving pool. Adding more pods did not immediately help: each new pod was exposed to the same excess traffic before it could contribute much useful work.

The team recovered by stopping traffic, scaling capacity substantially, and then restoring traffic gradually. Once the service could make progress again, the backlog began to drain. Eventually traffic returned to its normal level.

There are details to investigate in any real incident like this. Was the first trigger a traffic spike, a short outage, or a downstream slowdown? Where did the waiting requests accumulate? Which health check caused a restart? But the feedback loop is recognizable: less useful work gets done, more work waits, and the work that waits makes recovery harder.

### System B: busy, but working

System B was also exposed to traffic above its capacity for hours. I was able to keep its CPU near 99% while maintaining low latency and as much useful throughput as the service could deliver. The high percentiles of latency increased somewhat, but remained within the service objective. Memory stayed bounded, and new pods could join and start serving. Excess requests were rejected quickly. In that system, the response happened to be `429`.[^status]

From the outside, both systems were very busy. One stopped being useful. The other kept doing about as much useful work as it could.

Why?

My answer is that System B controlled the boundary between *offered work* and *admitted work*. System A allowed too much work to cross that boundary, including work that had little chance of finishing in time. The part I like most is that this is the service's responsibility. I should not need every caller to guess how many requests my service can survive. We need a little queueing theory to see how to make that responsibility real.

## There is always a queue

Start with a small asynchronous service. It receives a request and spawns a coroutine. There is no `Queue` object in the code, so it can look as though the service does not queue requests at all.

At low traffic this impression may hold. At higher traffic, more coroutines become runnable at the same time. They compete for CPU cores. Others wait for sockets, connection pools, locks, a GPU slot, or a downstream response. The work is waiting somewhere, even when nobody called the place where it waits a queue.

The same thing happens with disk access. A request that reads a large amount of data can occupy the disk while another request waits. If traffic arrives in bursts, the next request may arrive before the previous one releases the resource. The disk did not gain capacity because the code used an asynchronous API.

One useful way to see the waiting work is [Little's Law](https://pubsonline.informs.org/doi/abs/10.1287/opre.9.3.383):

\[
L = \lambda W
\]

Here \(L\) is the average number of requests in the system, \(\lambda\) is the rate flowing through it, and \(W\) is the average time a request spends there. In a stable system, that flow rate equals both the long-run entry and exit rates.

Suppose a stable service completes 100 requests per second and each request spends an average of 200 milliseconds in the service. On average, 20 requests are present. They are not necessarily all running on CPU. Some may be waiting on an API, a lock, or a connection. Little's Law describes the long run average for a stable flow; it does not say that the service can accept any arrival rate or that all 20 requests are executing in parallel.

The same relationship turns up elsewhere. Suppose a network path can deliver 100 MB/s and its round trip time is 20 milliseconds. Its bandwidth-delay product is 2 MB: approximately that many bytes must be in flight to fill the path. If a 10 MB burst reaches a 100 MB/s bottleneck while the path is otherwise busy, about 8 MB beyond that in-flight amount can wait, adding roughly 80 milliseconds of serialization delay to the back of the burst. This ignores packet scheduling, competing flows, and protocol behavior, but it shows where the extra time comes from. Message throughput multiplied by processing time similarly gives work in progress. If you do not know where this work is waiting, that is a reason to look for it, not evidence that it does not exist.

> Making a queue invisible does not make it disappear.

## What exactly is at capacity?

We often say a service can handle "100 requests per second." That is useful shorthand, but it hides the reason the limit exists. One request may need 2 milliseconds of CPU; another may need 200. One may use a small amount of memory; another may hold a database connection while waiting for a slow client.

It helps to separate a few terms:

- **Throughput** is completed useful work per unit of time.
- **Concurrency** is work in progress, including work that is waiting.
- **Parallelism** is work the available resources can actually execute at the same time.
- **Capacity** is the sustainable rate at which those resources can finish useful work within the service objective.
- **Offered load** is all the work callers attempt to send. **Admitted load** is the portion we accept for processing.

For a CPU bound stage, we can begin with CPU time per request, \(S_{cpu}\). If the stage admits \(\lambda\) requests per second, the CPU demand is approximately \(\lambda S_{cpu}\) CPU seconds per second. Across \(m\) equally usable cores, estimated utilization is:

\[
\rho = \frac{\lambda S_{cpu}}{m}
\]

Here \(\rho\) is CPU utilization: the fraction of those \(m\) cores' total capacity that the admitted work demands.

How do we get that 20 milliseconds? Over a representative, approximately steady 60-second window, suppose four cores use 120 CPU seconds *attributable to 6,000 successfully completed requests*. Then:

\[
S_{cpu} \approx \frac{120\ \text{CPU seconds}}{6{,}000\ \text{useful completions}}
= 0.020\ \text{CPU seconds per request}
\]

Subtract unrelated background work before calculating this number. If rejected or failed attempts consume significant CPU, measure and account for that separately; otherwise the ratio is not the CPU demand of a successful request. Use a workload mix representative of the traffic you expect, because a single average hides expensive request classes.

At 100 requests per second and 20 milliseconds of CPU time per request, demand is two CPU seconds each second. On four cores, that is roughly 50% utilization. The CPU-only ceiling, before overhead or a latency objective, would be \(4/0.020=200\) requests per second. If the total wall time is 200 milliseconds, Little's Law still says about 20 requests are in the system. On average, only about two core equivalents are executing their CPU work. The rest of the elapsed time is spent elsewhere.

This calculation is intentionally simple. Real requests have different costs, cores are not always interchangeable, and a GPU or database connection pool has its own constraints. The point is to measure the resource that limits *this* stage. Adding coroutines does not add cores. Adding pods does not help if every pod is blocked on the same database. Adding GPU cards helps only if useful work reaches them and finishes before its deadline.

## Why things get strange near saturation

Utilization is one way to describe load. For a queue that can finish \(\mu\) units of work per second while \(\lambda\) units are admitted each second, I find it more useful to ask how much **slack** remains:

\[
\text{slack} = \mu - \lambda
\]

If the service can finish 100 requests per second and receives 90, it has room to catch up at 10 requests per second after a burst. At 99 arriving requests per second, it has room to catch up at only one. The two cases sound similar when reported as "90%" and "99%" utilization, but they behave very differently after a backlog forms.

If there are \(Q\) requests waiting and arrivals remain below capacity, a simple estimate for the time needed to remove that backlog is:

\[
T_{\text{drain}} \approx \frac{Q}{\mu - \lambda}
\]

Here \(Q\) is the backlog, and \(\mu-\lambda\) is the spare completion rate available to drain it.

For a backlog of 1,000 requests, 100 requests per second of capacity, and 90 arrivals per second, draining takes roughly 100 seconds. At 99 arrivals per second, it takes roughly 1,000 seconds. If arrivals exceed capacity, the backlog does not drain at all.

Waiting can rise much faster than utilization. In the simplest single server model with random arrivals and random service times, average queueing delay is proportional to \(\rho/(1-\rho)\), where \(\rho\) is utilization—the fraction of that server's capacity in use. That factor is 9 at 90% utilization, 19 at 95%, and 99 at 99%. These are properties of that model, not multipliers to paste into a production dashboard.

For a more general single server queue, [Kingman's heavy traffic approximation](https://rss.onlinelibrary.wiley.com/doi/pdf/10.1111/j.2517-6161.1962.tb00465.x) adds the variability of arrivals and service times:

\[
W_q \approx \frac{C_a^2 + C_s^2}{2}
\frac{\rho}{1-\rho}\,\mathbb{E}[S]
\]

Here \(W_q\) is average time waiting in the queue, \(\mathbb{E}[S]\) is average service time, and \(\rho\) is utilization of this single server. \(C_a\) and \(C_s\) are the coefficients of variation of interarrival and service times: standard deviation divided by mean. Consider a *separate, single-server stage* with mean service time of 10 milliseconds and utilization of 90%. If both coefficients are 1, the variability factor is 1 and the estimated mean queue wait is 90 milliseconds. If arrivals still have \(C_a=1\) but service has \(C_s=2\), the factor is 2.5 and the estimate becomes 225 milliseconds. Leaving out the factor implicitly assumes a value of 1; it does not assume zero variability. Multiple workers change the exact calculation; the classical Erlang C model is one starting point when its assumptions fit. For production decisions I would measure the latency distribution and load test the real system rather than pick a universal CPU threshold from a textbook.

This explains why "keep CPU below 70%" can be sensible for one service and wasteful for another. The target depends on burst size, request cost, the latency objective, and how quickly capacity can be added. It is not a law of nature. In our four-core example, suppose load tests show that the latency objective holds through 85% CPU for this mix of requests. That gives an initial *safe* throughput estimate of \(0.85(4)/0.020=170\) useful requests per second, below the 200/s CPU-only ceiling. We will use 170/s to size waiting and scaling, then test rather than treat it as a guaranteed rate.

## Move the waiting to a place you control

Once we know that waiting exists, we can decide where it is allowed to happen.

```text
request → admission check → bounded wait → worker slot → scarce resource
```

The worker-slot limit prevents more work from occupying the scarce resource than it can safely handle. The bounded queue gives short bursts somewhere to wait. Admission decides whether a new request may join that queue at all. A request that cannot enter can be rejected before it consumes much CPU, memory, a GPU slot, or downstream capacity.

Where should the concurrency limit come from? Measure how much of the limiting resource a request consumes and what happens to latency as concurrent work grows. In our four-core example, 170 completions/s at 200 milliseconds of wall time would imply about 34 requests in the system, *if wall time remains the same*. Trying an in-flight limit around 40 could be a starting experiment, not a derived optimum: wall time and request mix may change near 85% CPU. For a GPU service, measure slots, batch behavior, and memory. For a database bound service, measure connection occupancy and the database's own useful throughput. Then load test around the proposed limit. A static number taken from the number of threads is usually a poor substitute.

Queue size should come from a latency budget. If the resource completes \(\mu\) jobs per second and we can afford at most \(W_{q,\max}\) seconds of waiting, a first approximation is:

\[
Q_{\max} \approx \mu W_{q,\max}
\]

Here \(Q_{\max}\) is the proposed maximum number waiting, \(\mu\) is the completion rate, and \(W_{q,\max}\) is the wait budget.

At 100 completed requests per second and a 200 millisecond waiting budget, that is about 20 waiting requests. For our four-core service, 170/s and a 100 millisecond queue-wait budget suggest at most about 17 waiting requests. We might start with 16 and measure the resulting wait distribution. Neither number is a guarantee for a bursty workload. The high percentiles matter, and a request with a shorter remaining deadline may not be able to wait even that long.

A bounded channel is not enough if requests can accumulate while *trying to enter it*. In Tokio, for example, `send(...).await` waits for channel capacity. If I spawn one unrestricted task per arrival, I can still accumulate unbounded waiting tasks outside a channel of size 16. `try_send` fails immediately when the channel is full; awaiting `send` is appropriate only if the producers waiting on it are bounded or backpressure can propagate safely to them.[^tokio] Count every waiting population, not just the one with "queue" in its type name.

Admission changes the mathematical model, too. A finite internal system can remain bounded when offered arrivals exceed 170/s because it refuses some of them. Little's Law then applies to admitted jobs and their time until exit, counting completions and other exits consistently, not to all offered attempts. The excess work has not vanished: it was rejected, abandoned, or is waiting outside the service.

There are two different time questions here. With \(Q\) jobs waiting and \(\mu\) jobs completed per second, a newly arriving request may wait roughly \(Q/\mu\) before starting. The *whole backlog* shrinks at only \(\mu-\lambda\) jobs per second, where \(\lambda\) is the admitted arrival rate, so recovery takes roughly \(Q/(\mu-\lambda)\). Confusing the two can make an apparently modest queue look harmless.

A 10,000 item queue does not give us more throughput. It gives us permission to be 10,000 items behind. Sometimes that is exactly what we want: batch processing can tolerate a backlog and smooth a burst. Sometimes it converts excess demand into a slow failure that nobody notices until callers have already given up.

> Queues absorb variance. They do not create capacity.

## Do not accept work you already know will fail

Consider a client with a 15 second deadline calling a server with a 30 second timeout. If the client gives up at 15 seconds, the server may spend another 15 seconds doing work for somebody who is no longer listening. Under light traffic that is wasteful. Under heavy traffic those 15 seconds can occupy the resource that other requests need to finish.

The deadline should travel with the request. If the client has 15 seconds, service A may have only 12 seconds left by the time it calls B. By the time B calls C, perhaps seven remain. Each layer should use the *remaining* time, allow a margin for returning a response, and cancel work that no longer has a caller. Propagation needs to reach queued work and expensive downstream calls, not just the HTTP handler.

An admission decision can start with a simple question:

\[
\mathbb{E}[W_q] + \mathbb{E}[S] + \epsilon < D_{\text{remaining}}
\]

Here \(W_q\) is queue wait, \(S\) is service time, \(\mathbb{E}[\cdot]\) means an average, \(\epsilon\) reserves time to return the response, and \(D_{\text{remaining}}\) is the caller's remaining deadline.

If even the average cannot fit, reject now. Passing this test does *not* promise a p99 objective. For a deadline-miss target of \(\alpha\), the actual question is closer to:

\[
P(W_q+S+\epsilon\le D_{\text{remaining}})\ge 1-\alpha
\]

That is, the probability of finishing before the deadline should meet the chosen target of \(1-\alpha\).

We may implement that with measured quantiles or a calibrated heuristic rather than an explicit distribution. In either case, measure how often admitted requests miss their deadlines and adjust. A request may also expire *while waiting*. The queue needs a way to discard it before it reaches the scarce resource.

FIFO is an easy default, but it can leave a nearly expired request behind a long running job. Earliest deadline first (EDF) may help when deadlines differ. It can also starve work with long deadlines, and it cannot rescue a request whose remaining time is already too short. Scheduling and admission solve different parts of the problem.

### A circuit breaker can defend the caller's own resources

Circuit breakers are usually introduced as a way to stop hammering a failing downstream service. There is another useful way to think about them: **preemptively give up on work that is unlikely to succeed, before it wastes our own scarce capacity**.

Imagine a request that must call a slow dependency and then use an expensive GPU. Recent calls to the dependency are timing out, and the request has too little time left for the GPU step. Continuing to call the dependency holds a connection, consumes memory, and possibly occupies a worker. A breaker can open for this operation, fail fast, and let those resources serve work with a better chance of success. It should later allow a small number of probes through to detect recovery. A permanently open breaker is just a new failure mode.[^breaker]

This is related to deadline admission, but it uses different evidence. A deadline tells us whether enough time remains. A breaker uses recent outcomes to estimate whether a particular operation is likely to succeed. We may also return a cheaper degraded result if the contract allows it. In each case the purpose is to spend less on requests that are headed for failure.

### Rate limiters answer a different question

A rate limiter is useful when we need to enforce a **quota**: how much a user, tenant, API key, or class of work may consume over time. A token bucket, for example, can allow short bursts while enforcing a longer term allowance. This is how we prevent one client from consuming everyone else's share or enforce a product plan.

The quota might be 100 requests per minute, but 100 cheap requests and 100 expensive requests can have very different effects on a service. A quota does not tell us whether CPU, memory, or a GPU slot is available *right now*. Conversely, a concurrency limit can keep the service stable while still letting one tenant monopolize it. We often need both controls, with different metrics and different error semantics.

The distinction also affects HTTP responses. `429 Too Many Requests` describes a client exceeding a rate limit. `503 Service Unavailable` can describe temporary capacity exhaustion and can include `Retry-After`.[^status] System B used `429` for fast overload rejection. I would make the reason explicit in the response and dashboards, and choose the status code according to the API's documented contract. A client must know whether to back off, retry elsewhere, or stop.

## A service should remain useful under excess demand

The service property I want is simple to state:

> A component should remain stable when callers offer more work than it can process.

That does not mean it can complete arbitrary offered load. There is always a physical limit to how many packets the network and ingress path can receive or reject. Within the load range we design and test for, the service should keep admitted work within its limits and decline the rest cheaply.

The mechanisms now fit together. A quota controls allocation over time. Admission checks whether work is worth starting. A concurrency limit protects the scarce resource. A bounded queue absorbs temporary variation. Deadlines expire work whose value has vanished. A circuit breaker avoids predictable waste. A cheap rejection tells the caller that no work was accepted.

This also changes the caller. Before the service owns its boundary, each caller may end up carrying a guessed semaphore, a hand-tuned sleep, or a special case for how many requests the dependency can survive. Those guesses become stale whenever the service or workload changes. If the dependency protects itself and responds clearly, I can remove much of that babysitting. The caller still owns its own deadline, retry budget, idempotency, and decision about whether the work is worth doing. It no longer has to be the dependency's overload controller. That is a real simplification in a system with many callers.

At increasing offered load I would like to see this shape:

```text
offered requests       rise
useful throughput      approaches the service's capacity
latency of successes   stays within a known bound
memory and in flight   stay bounded
rejections             rise
```

Contrast that with System A, where useful throughput *fell* while resource consumption rose. A high CPU graph alone cannot distinguish the two. System B's CPU could sit near 99% while it made steady progress because the amount of admitted work remained controlled. That is not a recommendation to target 99% CPU in every service. It is a reason to judge health by useful throughput, latency, memory, and recovery behavior as well as utilization.

Stable machinery is not the same as fulfilled demand. If the service rejects half of eligible requests, it may be protecting itself correctly while users still have a serious problem. Alongside admitted-request latency, I would track:

\[
\text{demand fulfilled on time} =
\frac{\text{unique eligible requests completed before deadline}}
{\text{unique eligible requests offered}}
\]

Define "eligible" in the product contract and count each logical request once, not once per retry attempt. This metric makes unmet demand visible even when the successful requests look fast.

I would also change the way we describe a service's capacity. "It can handle about X QPS before it falls over" leaves the behavior after X undefined. A more useful contract has three parts:

1. **Capacity:** one unit of the service completes X useful requests per second within the latency objective, for a specified workload mix.
2. **Excess demand:** requests above admitted capacity receive a quick, predictable response without degrading the accepted requests.
3. **Retry:** the response tells callers when and whether a new attempt is appropriate. The operation is safe to retry, or the API explicitly says it is not.

The workload mix belongs in the first statement. Otherwise an increase in expensive requests can appear to be a mysterious loss of capacity even when the server is doing exactly the amount of work it could always do.

## Retries are expensive when failed attempts are expensive

"Retries cause retry storms" is a warning I hear often. It is incomplete. We need to ask how much scarce work a failed attempt performs.

\[
C_{\text{attempt}} = C_{\text{receive}} + C_{\text{parse}}
  + C_{\text{admission}} + C_{\text{partial work}}
\]

Each \(C\) is a cost measured in the same scarce resource for the named step. In particular, \(C_{\text{partial work}}\) is the work an unsuccessful attempt performs after admission.

If the first three steps are cheap and partial work is nearly zero, a retry after rejection may be a reasonable way for clients to wait outside the service. A different pod may have room, or capacity may arrive shortly. Google describes a version of this behavior in its discussion of [handling overload](https://sre.google/sre-book/handling-overload/): quick rejection can help retries find an available backend.

This is how I think of retries under a finite admission boundary: the unresolved logical requests form a waiting population *outside* the service. Each new attempt asks whether a slot is available yet. That population can be invisible to a server-side queue metric, but it is still waiting work. Keep separate counts for logical requests, retry attempts, and the resource cost of those attempts. Moving waiting outside the server is useful only if the new waiting loop is controlled.

If each failed attempt already used half a GPU inference, held a database lock, or called three dependencies, the same retry behavior can consume the capacity needed for recovery. A useful operational metric is:

\[
\text{retry waste ratio} =
\frac{\text{scarce resource spent on failed attempts}}
     {\text{total scarce resource spent}}
\]

Attempts alone are not the villain; wasted scarce work is. But even cheap attempts are not free. Rejection itself has a cost, and synchronized clients can overwhelm the ingress path. Clients need bounded attempts, a retry budget, jitter, and a deadline. They also need an idempotency contract when a timeout does not prove that the earlier operation failed.[^retries]

One subtle failure is retrying at every layer. If A retries B, and B retries C, a single user action can multiply into many calls to C. Decide which layer owns the retry. If a service knows retrying will not help, it should say so and let the error propagate. A `Retry-After` header is guidance, not permission for every client to wake up at exactly the same instant; clients should still avoid synchronized retries.

This is why cheap rejection and caller behavior have to be designed together. A retry can be a way to wait for capacity; an expensive or unbounded retry loop is a way to burn it.

## A message broker does not make the capacity deficit disappear

Now suppose the work arrives through Kafka or SQS rather than HTTP. The queue is explicit and often durable. That makes it easier to see, but it does not change the arithmetic.

For pending broker work, while a backlog exists and ignoring expiration, duplication, and redelivery:

\[
\frac{dQ}{dt} = \lambda - \mu
\]

Here \(Q\) is the number of records still pending processing, \(\lambda\) is the rate at which new records become pending, and \(\mu\) is the rate at which they are processed. This is not the total number of records retained in a Kafka log.

At 1,000 messages per second arriving and 800 completed, the backlog grows by 200 each second. An hour of that leaves roughly 720,000 additional messages. This queue depth is an accumulated capacity deficit. It is not a property of Kafka that more partitions or longer retention will erase on its own.

But a broker record is not always a unique piece of user work. If I draw a boundary around *all* unresolved logical jobs, including those waiting at callers, the accounting is different:

\[
\frac{dN_{\text{live}}}{dt}
= \lambda_{\text{new}}-x_{\text{successful}}-x_{\text{expired}}-x_{\text{abandoned}}
\]

Here \(N_{\text{live}}\) counts unresolved logical jobs, \(\lambda_{\text{new}}\) counts newly created jobs per second, and each \(x\) is a rate of jobs leaving through the named outcome. These exit categories must be disjoint; abandonment includes a terminal failure if we choose that definition. Retrying the same unresolved job does not add another logical job. It adds an attempt, which may consume resources. A retry that creates another broker message *does* add a physical record. Confusing those populations can make a dashboard report growing "demand" when the new records are actually repeated attempts at the same demand.

For that pending queue, if the deficit persists for \(T\) seconds, a rough estimate before expiration or dropping is \(Q_0+(\lambda-\mu)T\), where \(Q_0\) is the starting backlog and \(\lambda-\mu\) is its growth rate. A message TTL can bound the *useful* backlog only if expired work is actually discarded before expensive processing. Broker retention alone may leave old messages available long after they stopped mattering. Once completion rate \(\mu\) exceeds arrival rate \(\lambda\), the recovery estimate is again \(Q/(\mu-\lambda)\).

The number you should care about often is not queue depth by itself but the **age of the oldest useful item**. Ten thousand messages could represent ten seconds of work or an entire day. The deadline of the work determines whether either is acceptable.

This is where queue configuration becomes a business decision. An intrusion alert may be extremely valuable for the next few seconds and nearly worthless tomorrow. An ordinary notification may tolerate a few minutes. History enrichment may wait for hours. We should decide which work expires, which work can be delayed, and which work should be dropped rather than endlessly redriven. Only then should we choose worker counts, retention, and retry policy.

### Who gets the next slot?

FIFO is fair in arrival order, but arrival order may have little relationship to value. Strict priority can protect an emergency class, but it can starve ordinary work during a long emergency. Earliest deadline first favors urgent work, but a tiny low value task with a near deadline may jump ahead of a much more important task. Weighted fair scheduling and aging can reserve capacity and keep low priority work from waiting forever. Shortest job first can improve average latency while making large jobs miserable.

One way to reason about these choices is *value per unit of scarce work*. If class A gives twice the value at half the expected processing cost of class B, allocating the next slot to A may make sense. But expected cost and value are estimates, and a policy based only on that ratio can starve expensive work indefinitely. Deadlines, waiting time, and fairness still matter.

I am interested in probabilistic shedding here. Instead of a hard line where every request below one priority level is dropped, each class could begin shedding at a different congestion level and increase its rejection probability at a different slope. A class might also have a maximum drop probability. That policy gives selected work a *chance* to reach the hard admission gate; it does not create capacity. If 10,000 low-priority requests arrive each second, even an 80% drop probability passes 2,000/s toward a service that may finish only 100/s. The hard gate still has to bound total admitted work. And a nonzero probability of passing the first filter is not a guaranteed fair share: for that, reserve or schedule actual capacity. The probability curve can express preference for high-value or low-cost work, while the hard gate protects the machine.

The question to ask is: **what outcome is the scheduling policy trying to optimize?** Average latency, the most urgent deadline, total value, or a fair share for every tenant lead to different answers.

## Kubernetes cannot supply a missing congestion boundary

Return to System A. A pod becomes overwhelmed and stops responding in time. Its health check fails, it is removed or restarted, and the remaining pods receive more traffic. More traffic makes them slower, which makes their health checks more likely to fail. The system loses capacity at exactly the moment it needs more.

```text
pod stops making progress
→ fewer effective pods
→ more traffic per surviving pod
→ more waiting and failures
→ still fewer effective pods
```

Scaling up can help only after new pods start, become ready, and begin doing useful work. If every new pod accepts an unlimited amount of waiting work immediately, adding replicas may simply create more places for that work to pile up. The autoscaler is a control loop with a delay, not an instantaneous reserve of healthy capacity.[^kubernetes]

Kubernetes also distinguishes liveness from readiness. A liveness failure can restart a container; a readiness failure stops normal traffic from being routed to it. A busy pod should usually be able to answer a cheap health check. If temporary overload is treated as a reason to restart, the restart can make the traffic problem worse. Kubernetes explicitly cautions that badly designed liveness probes can cause cascading failures.[^kubernetes]

In a service that controls admission, losing a pod looks different. Total successes may fall until replacement capacity arrives. Rejections rise. Surviving pods continue to finish admitted work, so the deployment retains a stable base from which to recover. This is the distinction I meant earlier: **overloaded and unhealthy are not synonyms**. A service can be unable to accept another request while still being healthy enough to serve the work it has already accepted.

### Derive the scaling target

Suppose load testing tells us that one pod meets the latency objective up to 85% utilization for the measured workload mix. Why might the autoscaler target 65% rather than 85%? Because the target has to leave room for traffic growth while new pods start, as well as for failures.

If the largest expected increase in traffic during the scaling delay is a factor of \(B\), a simple starting condition is:

\[
\rho_{\text{target}} \leq \frac{\rho_{\max}}{B}
\]

Here \(\rho_{\text{target}}\) is the desired utilization before the burst, \(\rho_{\max}\) is the highest utilization that met the latency objective in testing, and \(B\) is the largest expected multiplier in traffic before new capacity is ready.

With an 85% safe limit and a possible 30% increase before capacity arrives, `0.85 / 1.3 ≈ 0.65`. In our four-core example, 65% means about 130 useful requests/s per pod at 20 milliseconds of CPU each. Ten pods could serve 1,300/s at that target. A 30% jump would be 1,690/s, just under their combined 1,700/s tested safe rate. But lose one pod during that jump and the remaining nine have only about 1,530/s of tested safe capacity. Admission still has to protect them while replacement capacity arrives. These are starting calculations, not proof of a real deployment's behavior.

Be careful when translating the percentage into a Kubernetes HPA setting. For CPU resource utilization, HPA's denominator is the pod's **CPU request**, not automatically its CPU limit or the node's cores.[^hpa] If our four-core pod requests four CPUs, 2.6 used CPUs reads as 65%. If it requests two CPUs, the same usage reads as 130%. The request configuration and actual resource limit must be part of the calculation.

Then ask what happens after a pod loss, a node loss, or an availability zone loss. How much capacity remains? Can the surviving units reject excess work without collapsing? Scaling policy and per-pod self-defense answer different parts of the same question. A load test at 2× or 10× offered traffic is often more revealing than a clean HPA graph from a normal afternoon.

## Revisit the two systems

We can now explain why the two services with similar CPU usage behaved so differently.

System A accepted or accumulated more work than it could complete. Some of that work waited in places that were not well controlled. As latency rose, callers timed out or retried. Work that had lost its caller could still consume resources. Pods under pressure stopped making useful progress; restarting them reduced effective capacity and sent yet more work to the survivors. The particular trigger and each causal link need incident data, but this feedback loop explains why removing traffic, adding capacity, and reintroducing work gradually could restore useful progress.

System B held the boundary. Its concurrency and waiting work remained bounded. Requests that could not be served were declined early. Its cost of saying "no" was small compared with the cost of processing a request. The autoscaler could add pods without sacrificing the existing ones. Offered load rose above capacity, but admitted load stayed near the rate the service could finish. A CPU graph near 99% was consistent with a healthy service because the other indicators still showed useful progress and bounded state.

A separate GPU-backed service provides another test of the model. During a peak, timeouts and retries increased, Kafka lag grew, and doubling nominal GPU capacity still coincided with an eightfold fall in useful throughput. Recovery began only when organic traffic fell roughly fourfold overnight.

Hardware count alone cannot explain that outcome. The useful throughput of the system is the work that finishes in time and is still needed, not the raw number of GPU operations started. If requests spent too long waiting, if retries repeated expensive partial work, or if expired messages still reached the GPU, extra cards might not have put the system back in a stable region. Once arrivals fell below effective completion capacity, backlog could drain. Less old work and fewer retries would then free still more capacity, making the recovery accelerate.

The numbers to put next to one another are new logical requests/s, attempts/s, admitted requests/s, and useful completions/s. If attempts rise much faster than logical demand, investigate retry cost. If admissions exceed useful completions, inspect where work waits or expires. If Kafka's oldest *useful* item keeps aging despite more GPUs, the added hardware has not repaired the end-to-end capacity deficit. And if much GPU time goes to work that ultimately misses its deadline, raw device utilization is not useful throughput. These are checks, not claims that any one mechanism caused that incident. I would verify the causal steps against its timeline before presenting a root cause.

## When the service is already collapsing

The checklist below is for design review. On call, I would first find the boundary that is failing: compare unique offered work, retry attempts, admitted work, useful completions, rejection cost, oldest useful backlog age, and available capacity. Then change one pressure point and watch whether *useful completions recover* while latency and waiting shrink.

- If repeated attempts are doing expensive partial work, fail them earlier or temporarily reduce that retry path; verify that wasted CPU or GPU time falls. Do not stop cheap, bounded retries merely because their count is high.
- If stale requests or broker messages are consuming slots, enforce deadlines and discard expired work before the scarce resource; verify that oldest useful age and deadline misses fall.
- If cheap rejections themselves saturate ingress, throttle or shed farther upstream; verify that accepted work keeps finishing and ingress latency falls. Per-pod admission cannot defend an already saturated network edge.
- If capacity was lost, restore healthy units or reduce offered work long enough to regain progress; verify that ready units stay ready and the backlog begins to drain. When arrivals remain above completion capacity, adding a small number of pods may not be enough.

Every intervention should be judged against the same outcome: more unique eligible work completed on time, not merely a prettier CPU graph.

## A checklist to take to work tomorrow

I would use the following questions to review a service. They are short enough to ask during a design review and concrete enough to test.

1. **Know the scarce resource.** Is it CPU, GPU time, memory, a connection pool, disk throughput, or a downstream limit? How much of it does each request class consume? What useful throughput does one capacity unit provide within the latency objective?
2. **Control admission.** Is work in progress bounded? Is waiting bounded? Can we decline excess requests *before* expensive work begins? What does a declined request cost?
3. **Respect time.** Does the caller's deadline reach every layer? Can queued work expire? Do we reject work that cannot finish before its deadline? Does cancellation release the scarce resource promptly?
4. **Make failure cheap.** Can a breaker or degraded response avoid an operation that is likely to fail? Do retries have budgets, jitter, deadlines, and an idempotency story? How much scarce capacity goes to failed attempts?
5. **Separate capacity from quota.** Which limits protect the service right now, and which quotas allocate capacity among callers over time? Do `429` and `503` mean different things in the API and the dashboards?
6. **Treat queued work as a promise.** How old is the oldest useful item? Which messages can wait, which expire, and which should never be redriven? Who decides which class gets the next slot?
7. **Derive scaling from the objective.** What utilization is safe for latency? How much can traffic grow before new pods are ready? What happens after a pod, node, or zone fails?
8. **Test the overload contract.** At 2×, 10×, and the largest credible burst, do useful throughput, successful latency, memory, and pod health remain stable? Do rejections rise in the expected way?

My favorite single test is this: **if callers accidentally send ten times your capacity tomorrow, will your service become less useful, or will it keep serving its capacity and decline the rest?**

## Own the congestion boundary

The component closest to a scarce resource is usually in the best position to defend it. Callers decide whether another attempt is valuable. A queue decides how long to retain work and which work goes first. An autoscaler adds capacity after a delay. The service decides what it can safely admit *now*.

I do not want every caller to know how to keep my service alive. I want my service to own that problem. Once it does, callers can make decisions about their own deadlines and the value of their work instead of compensating for my service's fragility. We cannot prevent excess demand; we can decide whether it turns into collapse. That is the shift from hoping the system will survive a peak to making its behavior under a peak part of the design.

[^status]: The service in the opening incident used `429` for overload. [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html) defines `429` for a client that has sent too many requests in a given time. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) defines `503` for temporary server overload or maintenance and permits `Retry-After`. The choice affects client behavior and monitoring, so it should be explicit in the API contract.
[^breaker]: The standard [circuit breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) uses recent failures to skip operations likely to fail, then probes for recovery. The same early decision can protect the calling component's own threads, connections, memory, and CPU time.
[^retries]: See Google's [handling overload](https://sre.google/sre-book/handling-overload/) for retry budgets and behavior under widespread overload, AWS on [backoff with jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), and AWS on [idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
[^kubernetes]: Kubernetes documents the timing of [horizontal pod autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) and the different effects of [liveness and readiness probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/).
[^tokio]: Tokio's [`Sender::send` documentation](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html) says it waits for channel capacity, while [`try_send`](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html#method.try_send) returns immediately if the buffer is full.
[^hpa]: Kubernetes [defines CPU resource utilization as a percentage of the requested CPU](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/#algorithm-details).

<!-- Before publication, verify the incident figures, the author's personal role in System B, and the GPU incident's causal chain against the original operational notes. The opening uses the author's Kubernetes and HTTP-status details; the GPU example comes from the earlier outline. -->
