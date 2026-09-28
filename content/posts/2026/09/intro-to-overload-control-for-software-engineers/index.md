---
title: "Intro to Overload Control for Software Engineers"
date: 2026-09-27T21:48:07-07:00
publishDate: 2026-09-27T21:48:07-07:00
draft: false
author: Anton Golubtsov
summary: "Why one busy service collapses while another keeps working, and how to build the second kind."
toc: true
math: true
tags:
    - Software Development
    - Distributed Systems
    - Queueing Theory
---

I've spent much of my career working on systems that process large volumes of user requests. I have seen some of them survive sustained traffic far above their capacity. Others fell apart at a load they should have been able to handle. The difference was rarely explained by the number of pods or the programming language.

Let me start with two systems.

### System A: total collapse

System A was a fairly standard service running in Kubernetes and handling client requests. It received a request, did some work, called other services, and returned the result. Autoscaling added pods when load increased. This had worked well enough through ordinary peaks.

Then incoming traffic reached roughly five times the service's maximum capacity. Kubernetes scaled the deployment to its configured limit. CPU was saturated and memory was exhausted, useful throughput fell close to zero, and new pods began restarting soon after they joined the serving pool. Adding more pods did not immediately help: each new pod was exposed to the same excess traffic before it could contribute much useful work.

The team recovered by stopping traffic, scaling capacity substantially, and then restoring traffic gradually. Once the service began completing requests again, the backlog began to drain. Eventually traffic returned to its normal level.

There are details to investigate in any real incident like this. Was the first trigger a traffic spike, a short outage, or a downstream slowdown? Where did the waiting requests accumulate? Which health check caused a restart? But the feedback loop is recognizable: less useful work gets done, more work waits, and the work that waits makes recovery harder.

### System B: busy, but working

System B was also exposed to traffic above its capacity for hours. I was able to keep its CPU near 99% while maintaining low latency and as much useful throughput as the service could deliver. The high percentiles of latency increased somewhat, but remained within the service objective. Memory stayed bounded, and new pods could join and start serving. Excess requests were rejected quickly. That system used `429` for the rejection response.[^status]

Both systems were heavily loaded, but their results were very different. Useful throughput fell close to zero in the first and stayed near capacity in the second.

System B limited how much work it accepted, distinguishing between *offered work* and *admitted work*. System A accepted too much, including requests with little chance of finishing in time. What matters to me is that the service owns this limit. I should not need every caller to guess how many requests my service can handle.

If you want a faster route through the article, read [There is always a queue](#there-is-always-a-queue), [A service should remain useful under excess demand](#a-service-should-remain-useful-under-excess-demand), and [Putting everything together](#putting-everything-together), then take the [self-defense checklist](#a-self-defense-checklist) into your next design review. The sections between them show how I arrived at the limits and what can go wrong at each boundary.

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

The same relationship turns up in a network. At 100 MB/s and a 20-millisecond round trip time, about 2 MB must be *in flight* to fill the path. That is data in transit, not a buffer allowance for a future burst. Separately, if 8 MB is already queued ahead of a packet at a 100 MB/s FIFO bottleneck, that packet waits roughly 80 milliseconds before transmission. In-flight data and queued data are different populations, just as requests in progress and requests waiting to start are.

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

How do we estimate CPU time per request? Over a representative, approximately steady 60-second window, suppose four cores use 120 CPU seconds *attributable to 6,000 successfully completed requests*. Then:

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

This is why "keep CPU below 70%" can be sensible for one service and wasteful for another. The target depends on burst size, request cost, the latency objective, and how quickly capacity can be added. It is not a law of nature. In our four-core example, suppose load tests show that the latency objective holds through 85% CPU for this mix of requests. That gives an initial *safe* throughput estimate of \(0.85(4)/0.020=170\) useful requests per second, below the 200/s CPU-only ceiling. We will use this estimate to size the queue and plan scaling, then test it. It does not yet guarantee that workers can keep taking requests from the queue at that rate.

### A closer look at variability

The simple utilization factor leaves out a detail that matters under bursty traffic: how unevenly work arrives and how much its cost varies. You can carry on to the spike example with the tested 170/s estimate; the next calculation explains why two services at the same average utilization can have very different waits.

For a more general single server queue, [Kingman's heavy traffic approximation](https://rss.onlinelibrary.wiley.com/doi/pdf/10.1111/j.2517-6161.1962.tb00465.x) adds the variability of arrivals and service times:

\[
W_q \approx \frac{C_a^2 + C_s^2}{2}
\frac{\rho}{1-\rho}\,\mathbb{E}[S]
\]

Here \(W_q\) is average time waiting in the queue, \(\mathbb{E}[S]\) is average service time, and \(\rho\) is utilization of the single server. \(C_a\) and \(C_s\) describe how uneven the arrival and service times are: each is its standard deviation divided by its mean.

To see what that variability costs, consider a *separate, single-server example*, not our four-core service. With a 10-millisecond mean service time and 90% utilization, \(C_a=C_s=1\) gives about 90 milliseconds of average queue wait. Keep the arrivals the same but raise \(C_s\) to 2, and the estimate becomes 225 milliseconds. The shorter expression \(\rho/(1-\rho)\) implicitly uses a variability factor of 1; it does not assume that arrivals or service times have no variation. For a real multi-worker service, I would measure the latency distribution under load rather than transplant this single-server result.

### Turn a spike into a requirement

An average arrival rate hides the shape of a spike. Our four-core service met its latency objective at 170 requests/s and normally receives 130. To estimate a waiting queue, I need one more assumption: in this simplified example, workers continue taking about 170 requests/s from that queue during the burst. The load test alone does not prove that departure rate under overload. The service might start more work that finishes too late, or contention might make it start less.

Now suppose arrivals climb to 200 requests/s for ten seconds. If the request mix stays the same and the queue starts empty, accepting 30 more requests each second than workers take leaves us with 300 waiting when the burst ends. The peak rate alone does not tell us that; its duration matters too. In general, with peak arrival rate \(\lambda_{\text{peak}}\), modeled queue departure rate \(\mu\), and spike duration \(T_{\text{spike}}\):

\[
Q_{\text{spike}}\approx\max(0,\lambda_{\text{peak}}-\mu)T_{\text{spike}}
\]

Here \(Q_{\text{spike}}\) is the backlog we would create by accepting the whole burst under that departure-rate assumption. Once traffic settles back to its normal rate of \(\lambda_0=130\) requests/s, we have \(H=\mu-\lambda_0=40\) requests/s of spare capacity to work it off. Draining those 300 requests therefore takes roughly \(Q_{\text{spike}}/H=7.5\) seconds. A request joining the back of the queue just as the burst ends could wait about \(300/170=1.8\) seconds before it starts—far from a 100-millisecond queue-wait budget.

Now we can ask how much of the spike we can afford to hold. If workers take about 170 requests/s from the queue, a 100-millisecond queue-wait budget suggests room for about 17 waiting requests. A one-second recovery deadline would allow a backlog of 40, because workers take 40 more requests/s than normally arrive. Latency is the tighter constraint. If \(Q_{\text{buffer}}\) is the physical queue size, \(W_{q,\text{budget}}\) is the wait budget, and \(T_{\text{recover}}\) is the recovery deadline, we can use the following starting bound:

\[
Q_{\text{allowed}}\lesssim
\min\!\left(Q_{\text{buffer}},\ \mu W_{q,\text{budget}},\
H T_{\text{recover}}\right)
\]

That is the sort of requirement I would write down: with 130 requests/s of normal traffic, handle a ten-second burst at 200/s while keeping admitted-request p99 latency within its objective and returning the queue to normal within one second. The arithmetic shows why we cannot accept every request under that contract. We need to add capacity, defer work elsewhere, or decline excess requests quickly.

The backlog estimate does not prove the p99 promise. A queue can drain as workers start requests even if those requests later finish after their deadlines. If \(D_{\text{SLA}}\) is the end-to-end latency target, we still need:

\[
P(W_q+S+\epsilon\le D_{\text{SLA}})\ge0.99
\]

Here \(W_q\) is queue wait, \(S\) is service time, and \(\epsilon\) covers response overhead. A burst with a more expensive mix of requests can reduce the safe completion rate, so we have to test the actual burst shape and request-cost distribution. We should also count how much unique offered work finishes on time; good latency after rejecting most of the demand is not the whole story.

## Admission control: make the waiting explicit

The spike calculation tells us what happens if we accept everything: by the end of those ten seconds, about 300 extra requests are still somewhere in the service. Imagine that the HTTP handler creates a coroutine for each arrival. Some requests may be ready to use CPU, while others are parked behind a connection pool or waiting for a worker permit. They are all unfinished work, even if none appears in a metric named "queue length." The waiting is real; we have simply let other parts of the runtime decide where it happens.

We need to make that decision before launching expensive work or allowing a request to wait without a limit. Each arrival can take a slot for started work, take a place in a bounded waiting queue, or be refused quickly when both are full:

```text
request → admission check
          ├─ active slot available → start work
          ├─ queue space available → bounded wait → active slot
          └─ neither available → reject
```

The queue limit caps requests waiting to start. The active-work limit caps requests that have started but have not finished; some may be using CPU, while others hold a connection or wait on I/O. Four CPU cores do not tell us how many such requests can safely overlap, and neither does a throughput estimate of 170 requests/s. I would try different limits under load and choose one that keeps admitted-request latency within its objective without leaving useful capacity idle.

To see the distinction, imagine a toy limit of six started requests and two waiting places. Those are not sizing recommendations; each letter below is a request, not a worker thread:

```text
started work (limit: 6)
  on four CPU cores:  [A] [B] [C] [D]
  waiting on I/O:     E   F

waiting to start:    [G] [H]          (queue limit: 2)
next arrival:         I → reject
```

For the waiting queue, I might start at 16 slots rather than the estimated 17, then measure the latency distribution under bursts. A request close to its deadline may need to be declined even when a slot is free.

A bounded channel is not enough if requests can accumulate while *trying to enter it*. In Tokio, for example, `send(...).await` waits for channel capacity. If I spawn one unrestricted task per arrival, I can still accumulate unbounded waiting tasks outside a channel of size 16. `try_send` fails immediately when the channel is full; awaiting `send` is appropriate only if the producers waiting on it are bounded or backpressure can propagate safely to them.[^tokio] Count requests at every place they can wait, including those outside an explicit queue.

These limits change the mathematical model, too. A service with finite capacity can keep its internal workload bounded even when arrivals exceed 170/s, because it rejects some requests. Little's Law then applies to admitted work and the time until it leaves the system. Successful completions and other outcomes must be counted consistently; the calculation cannot use the entire offered arrival rate. The excess work has not vanished: it was rejected, abandoned, or is waiting outside the service.

A queue with room for 10,000 items does not increase throughput. It allows a backlog of up to 10,000 unprocessed items. Sometimes that is exactly what we want: batch processing can tolerate a backlog and smooth a burst. Sometimes it converts excess demand into a slow failure that nobody notices until callers have already given up.

> Queues absorb variance. They do not create capacity.

### A closer look at worker-pool handoffs

Separate CPU and I/O pools let us manage the use of those resources independently, but it is easy to create a new queue without noticing. Request A leaves a CPU worker to do I/O, and that worker takes request B from the input queue. Suppose the CPU queue has two places, request D arrives while A is waiting, and B is still using CPU when A's I/O completes:

```text
                    A on CPU       A on I/O       A needs CPU again
CPU worker          [A]            [B]            [B]
I/O wait             -             [A]             -
CPU queue (2)       [B] [C]        [C] [D]        [C] [D]
outside queue        -              -             [A: resume]
```

A did not finish when it left the CPU worker, so it should still count against the started-work limit. Once its I/O completes, it needs CPU time to process the result, but both queue places are full. Its continuation now waits *outside* the bounded input queue. If it joins the same FIFO queue when space opens, C and D are already ahead of it.

I have seen three ways to arrange this. A strictly sequential pipeline can have a pool and bounded queue for each stage—CPU, I/O, post-processing CPU, perhaps another I/O stage—with sizes and backpressure tuned together.

A shared CPU pool can raise a request's priority on each hop. When a completed I/O operation and a new request are both waiting for CPU, the continuation goes first. That lets ready work already in the system drain before the pool starts fresh work. It does not stop the pool from taking a new request while older ones are still waiting on I/O; refusing new admissions until *all* started work finishes would be a separate rule.

The simpler option for an asynchronous service is often one CPU pool with nonblocking I/O and a separate limit on *all* started requests, including those waiting on the dependency.

That last limit can be larger than the number of cores without requiring more CPU threads. If a request uses 10 milliseconds of CPU and waits 100 milliseconds for I/O, roughly 11 requests per core could be in flight in an ideal steady state. This assumes the I/O dependency can sustain the corresponding throughput; if it slows down, more in-flight work just becomes more waiting. I would bound calls to that dependency separately and use a circuit breaker when timeouts show that continuing is likely to waste work. Core count, CPU time, I/O latency, and useful throughput give us a starting point; [adaptive concurrency limiters](https://github.com/Netflix/concurrency-limits) can adjust the bound from observed latency. They still need safe bounds and load tests.

The handoff creates another place where waiting must be bounded, while the admission limit still applies. Even after we have bounded every waiting place, we still have to ask whether a request inside it can produce a useful answer. A free slot is worth little if the work we put into it will miss its deadline or fail downstream.

## When work is unlikely to succeed

Consider a client with a deadline of 15 seconds calling a server with a timeout of 30 seconds. If the client gives up at 15 seconds, the server may spend another 15 seconds doing work for somebody who is no longer listening. Under light traffic that is wasteful. Under heavy traffic those 15 seconds can occupy the resource that other requests need to finish.

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

FIFO is an easy default, but it can leave a request close to its deadline behind a long-running job. Earliest deadline first (EDF) may help when deadlines differ. It can also starve work with long deadlines, and it cannot rescue a request whose remaining time is already too short. Scheduling and admission solve different parts of the problem.

### A circuit breaker should defend the caller's own resources

Circuit breakers are usually introduced as a way to stop hammering a failing downstream service. For overload control, that is only half their job. **When a dependency is required, its breaker must inform admission control before we start expensive work.** Otherwise it may protect the dependency without protecting this service.

Suppose a request needs ten seconds of CPU preparation before calling that dependency. If the breaker was already open but we check it only at the call site, we spend those ten seconds on a request that cannot finish. Failing then may cause the caller to retry and repeat the CPU work. Waiting for the dependency or retrying inside the service keeps an active slot occupied while the queue grows and the deadline shrinks.

Before processing begins, the admission check should consult the same breaker or overload signal. New requests can then be refused before the CPU step, or processed at lower cost with a reduced result if the contract permits. Keep the call-site check too: the dependency can fail after admission, and running requests still need deadlines and cancellation. The breaker also needs a small number of probes to detect recovery; a breaker that never checks for recovery can itself prevent the service from recovering.[^breaker]

A deadline and a breaker offer different evidence at the same admission boundary. The first asks whether enough time remains; the second uses recent outcomes to judge whether a required operation is likely to succeed. Neither is a promise, but together they help reserve scarce capacity for work with a plausible path to a useful result.

## A service should remain useful under excess demand

This is what I want from a service:

> A component should remain stable when callers offer more work than it can process.

That does not mean it can complete arbitrary offered load. There is always a physical limit to how many packets the network and ingress path can receive or reject. Within the load range we design and test for, the service should keep admitted work within its limits and decline the rest cheaply.

### Quotas are not capacity limits

Protecting the machine is not the only reason to say no. We may also need to decide how much a user, tenant, or API key is entitled to consume over time. That is a **quota**. A token-bucket rate limiter can allow a short burst while enforcing a longer-term allowance, keeping one caller from taking everyone else's share.

**Quotas and rate limits can reduce overload, but they are not a substitute for admission control based on the resources available now.** A quota of 100 requests per minute tells us little about the cost of those requests or whether a GPU slot is free *right now*.

Imagine a multi-tenant service sized for the sum of its provisioned quotas at the usual query cost. One tenant stays within its quota but begins sending much more expensive queries. The request count is still allowed, while its CPU demand rises. Or a downstream service slows down: at the same admitted rate, requests spend longer in flight, using more memory and perhaps holding connections. As completions fall behind arrivals, queues build. Every tenant can be within quota while the service is already overloaded.

The service still needs limits on active work and waiting, with admission decisions tied to the resource that is actually scarce. Those limits protect it when query cost or dependency latency changes. Conversely, a concurrency limit may keep the service stable while one tenant takes every available slot. Quotas handle allocation; capacity controls handle what the service can safely take on.

The distinction should reach the API. `429 Too Many Requests` describes a client exceeding a rate limit; `503 Service Unavailable` can describe temporary capacity exhaustion and can include `Retry-After`.[^status] System B used `429` for fast overload rejection. Whatever the status code, the response and dashboards should make the reason clear so a client knows whether to back off, retry elsewhere, or stop.

When a service controls admission and explains its rejections clearly, callers have less work to do. Otherwise, each caller may need a semaphore with an estimated limit, manually chosen delays, or special rules based on the assumed capacity of the dependency. Those guesses become stale whenever the service or workload changes.

If the dependency protects itself and responds clearly, many of those caller-side limits are no longer needed. The caller still owns its own deadline, retry budget, idempotency, and decision about whether the work is worth doing. It no longer has to be the dependency's overload controller. That is a real simplification in a system with many callers.

At increasing offered load I would like to see this shape:

```text
offered requests       rise
useful throughput      rises, then holds near tested capacity
latency of successes   stays within a known bound
memory and in flight   stay bounded
rejections             rise
```

Contrast that with System A, where useful throughput *fell* while resource consumption rose. A high CPU graph alone cannot distinguish the two. System B's CPU could sit near 99% while it made steady progress because the amount of admitted work remained controlled. That is not a recommendation to target 99% CPU in every service. It is a reason to judge health by useful throughput, latency, memory, and recovery behavior as well as utilization.

I would plot unique requests offered per second, admissions, useful completions before the deadline, and quick rejections on the same timeline. Count each logical request once rather than inflating demand with retry attempts. If useful throughput rises and then holds steady as offered load grows, while successful latency and in-flight work stay bounded, the service is defending its capacity. If it rejects half the demand, users still have a capacity problem, even though the service itself has not collapsed. The two facts should be visible together.

Instead of saying **"It can handle about X QPS before it falls over"**, I would say **"For this workload mix, one unit can complete about X useful requests per second within the latency objective; excess load is rejected rather than allowed to degrade that throughput."** A bounded queue may absorb a short burst before rejection begins. The response should also tell callers whether a retry is appropriate; if it is, the API needs a safe retry policy.

The workload mix belongs in that sentence. Otherwise an increase in expensive requests can appear to be a mysterious loss of capacity even when the server is doing exactly the amount of work it could always do.

Quick rejection protects the service, but excess demand may remain. Work can return as a retry, wait in a broker, or wait for an autoscaler to bring new pods online. If the work still needs to be done, it is waiting somewhere else. Next, I want to look at what happens in each of those places.

## Cost of retries

“Retries cause retry storms” is too simple an explanation. A retry is another attempt at the same logical request; what matters is its cost and whether the work still has a chance to succeed. The caller and the receiving service pay different costs.

For the caller, the failed attempt's latency and any backoff before trying again both eat into the deadline. Another attempt adds traffic and may repeat an operation whose previous outcome is unknown. A timeout does not prove the first attempt failed, which is why the operation's idempotency contract matters.[^retries]

That caller may itself be a service with another caller waiting on it. Imagine 100 requests/s moving through A → B → C. If C's response time grows from 100 milliseconds to one second while it still completes the same rate, Little's Law says roughly 90 more requests remain in flight. If A and B each hold a request context until C replies, both now retain those extra requests in memory; their active-request counts rise even though arrivals have not.

A retry from B to C may be cheap for C to reject, but B's backoff keeps the upstream contexts alive longer. If C's completion rate also falls, a growing backlog adds to the problem. The cost of a retry is not only what the receiver does for that attempt.

Giving up can cost more than one well-placed retry. Suppose B looks healthy when A starts, but the call to B fails after A has spent ten seconds of CPU preparing input. If A retries B while its own caller still wants the answer, it may reuse that preparation. If A fails and its caller retries the whole operation, those ten seconds of CPU work may have to be repeated, reducing useful throughput. That argues for a local retry only while the deadline leaves room and B has a plausible chance of recovering. If B is overloaded, repeated calls may just occupy A's slot and deepen congestion; the ten seconds already spent are not a reason to keep trying indefinitely.

We can also make that preparation reusable. A bounded cache keyed by the logical request can keep the prepared input for a later attempt. A shared cache such as Redis makes it available across pods; a local cache with sticky routing avoids the remote lookup, but a reroute or pod restart may force recomputation.

In an asynchronous pipeline, the expensive computation can be its own stage: publish its result, or a reference to it, to Kafka or SQS and let the next stage retry from there. A Flink job can recover prepared state from a checkpoint, though processing since the last completed checkpoint may replay. None of these handoffs eliminates duplication by itself; if duplicate effects matter, the output and the next stage need idempotent or transactional handling.[^stage-retry]

The choice is really about where the next attempt starts, and which work it must repeat:

```goat
   prepare: 10 s
        |
        v
      B fails
        |
   +----+-------------+--------------+
   |                  |              |
   v                  v              v
 retry B           retry A        save input
 reuse prep        redo prep      retry B later
```

Preserving work does not mean every layer should retry. If A retries B and B retries C, one user action can multiply into many calls to C. When choosing which component handles retries, consider both the multiplication of attempts and the cost of giving up. If a service knows another attempt will not help, it should say so rather than invite more work.

For the receiving service, the question is how much scarce capacity a failed attempt consumes. We can approximate its cost as:

\[
\begin{aligned}
C_{\text{attempt}} &= C_{\text{receive}} + C_{\text{parse}} \\
&\quad + C_{\text{admission}} + C_{\text{partial work}}
\end{aligned}
\]

Each \(C\) is a cost measured in the same scarce resource for the named step. In particular, \(C_{\text{partial work}}\) is the work an unsuccessful attempt performs after admission.

If the first three steps are cheap and partial work is nearly zero, the receiver can reject promptly when the limit on admitted work has been reached. The caller can back off and try again within its deadline; a different pod may have room, or capacity may arrive shortly. Google describes a version of this behavior in its discussion of [handling overload](https://sre.google/sre-book/handling-overload/): quick rejection can help retries find an available backend.

There is a useful distinction between **"I have no room for this request"** and **"my dependency has no useful capacity right now."** The first is a local decision by one receiver; the second is an inference a caller can make from repeated outcomes. One refusal does not prove that every pod is full, so a caller with time and a retry budget may find room elsewhere. If refusals become common across pods, repeatedly searching for a free one spends ingress capacity across the whole dependency without making much progress. The caller should back off or stop and let its own caller know. The dependency need not be literally down; it may be doing all the useful work it can.

This can work without a controller that knows the state of every pod. Each receiver defends its own finite capacity and reports a quick refusal; each caller adjusts from the outcomes it sees, within a deadline and attempt budget. Those bounds matter because a swarm of individually reasonable callers can still overwhelm the ingress path if all of them keep probing at once.

A late rejection changes the timing. Suppose a request spends 900 milliseconds in a hidden server queue before receiving an overload response. If the caller then backs off for 200 milliseconds, it has spent 1.1 seconds without making progress, and the server may have held memory or a slot throughout the first part. The backoff is the same in both paths; the hidden queue is the extra cost:

```goat
Prompt: attempt --> reject --> backoff 200 ms --> retry
Late:   attempt --> wait 900 ms --> reject --> backoff 200 ms --> retry
```

I think of work returning through retries as a queue *outside* the service: the logical requests are still unresolved and waiting for admission. Each new attempt asks whether a slot is available yet. Those requests can be invisible to a server-side queue metric, but it is still waiting work. Keep separate counts for logical requests, retry attempts, and the resource cost of those attempts. Moving waiting outside the server is useful only if waiting and retries in the new location are also bounded.

If each failed attempt already performed half the computation for a GPU inference, held a database lock, or called three dependencies, the same retry behavior can consume the capacity needed for recovery. A useful operational metric is:

\[
\text{retry waste ratio} =
\frac{\text{scarce resource spent on failed attempts}}
     {\text{total scarce resource spent}}
\]

The waste ratio tells us whether retries are burning the resource we are trying to protect, but cheap rejections can still add up. Every rejected attempt has to reach the service and pass through admission. If many callers retry together, those attempts can crowd out useful work even though each one is cheap.

After a rejection, the caller should honor `Retry-After` if supplied and spread its attempts out with jitter. The retry loop also needs to stop when its deadline or attempt budget runs out. Those limits let quick rejection move waiting to callers without creating an unbounded stream of new attempts.

## A message broker does not make the capacity deficit disappear

Now suppose the work arrives through Kafka or SQS rather than HTTP. The queue is explicit and often durable. That makes it easier to see, but it does not change the arithmetic.

For records waiting to be processed, ignoring duplication and redelivery, the queue changes when records arrive, workers take them, or we discard them:

\[
\frac{dQ}{dt} = \lambda - \mu - \delta
\]

Here \(Q\) is the number of pending records, \(\lambda\) is the rate at which new records arrive, \(\mu\) is the rate workers start processing them, and \(\delta\) is the rate records are discarded before processing. A logical job can expire without reducing \(Q\): its record leaves this queue only when we start or discard it. This is not the total number of records retained in a Kafka log.

At 1,000 messages per second arriving, 800 started by workers, and none discarded, the backlog grows by 200 each second. An hour of that leaves roughly 720,000 additional messages. This queue depth is an accumulated capacity deficit. More Kafka partitions or longer retention will not eliminate that deficit on their own.

The number of broker records does not necessarily match the number of user jobs. Retrying one unresolved job creates another attempt, not another logical job. If the retry publishes a new message, though, it *does* create another physical record. A dashboard can show growing "demand" when some of that growth is repeated attempts at work we already knew about.

An idempotency key becomes more useful when we check it *before* repeating expensive work. If the job already finished, a worker can acknowledge and discard the duplicate record, or reuse a stored result if downstream still needs it. That cheap path lets workers actively drain a backlog of duplicates instead of sending each one through the full computation again. The completion record must be retained long enough to recognize retries. For copies arriving together, an ordinary cache lookup is not enough: workers need an atomic claim to avoid duplicate computation, and external side effects still need idempotent or transactional handling.

### A closer look at logical-job accounting

The pending-record equation tells us how many messages wait in the broker, not how many distinct jobs remain unresolved. If I draw a boundary around *all* unresolved logical jobs, including those waiting at callers, the accounting is different:

\[
\frac{dN_{\text{live}}}{dt}
= \lambda_{\text{new}}(t)-x_{\text{successful}}(t)-x_{\text{expired}}(t)-x_{\text{abandoned}}(t)
\]

Here \(N_{\text{live}}\) counts unresolved logical jobs, \(\lambda_{\text{new}}\) counts newly created jobs per second, and each \(x\) is a rate of jobs leaving through the named outcome. These exit categories must be disjoint; abandonment includes a terminal failure if we choose that definition. This is an accounting identity, not a claim that expiration is independent of earlier arrivals. If every job expires \(D\) seconds after arrival, the jobs expiring at time \(t\) came from the arrivals at \(t-D\), and only those not completed or abandoned in the meantime can expire. If every job from that group is still awaiting a result, \(x_{\text{expired}}(t)=\lambda_{\text{new}}(t-D)\); otherwise the expiration rate is smaller.

Retries of the same job change the number of attempts or records, not \(N_{\text{live}}\). This is why I would graph those counts separately.

### Decide whether the backlog is still useful

For the pending queue, if the deficit persists for \(T\) seconds, a rough estimate before discards is \(Q_0+(\lambda-\mu)T\), where \(Q_0\) is the starting backlog and \(\lambda-\mu\) is its growth rate. A job's deadline determines when it stops being *useful*; a broker TTL may remove its record, but broker retention alone may leave old messages available long after they stopped mattering. Workers still need to check the deadline and discard expired work before expensive processing. If workers can start and finish processing records at a rate \(\mu\) above the arrival rate \(\lambda\), with no further discards and steady rates, the recovery estimate is again \(Q/(\mu-\lambda)\).

The **age of the oldest useful item** often matters more than queue depth alone. Ten thousand messages could represent ten seconds of work or an entire day. The deadline of the work determines whether either is acceptable.

This is where queue configuration becomes a business decision. An intrusion alert may be extremely valuable for the next few seconds and nearly worthless tomorrow. An ordinary notification may tolerate a few minutes. History enrichment may wait for hours. We should decide which work expires, which work can be delayed, and which work should be dropped rather than repeatedly delivered without an end. Only then should we choose worker counts, retention, and retry policy.

### Who gets the next slot?

First consider jobs of one kind. FIFO takes the oldest job first. Suppose each job is useful for 30 seconds, but the one at the front has already waited 40. We should discard it before processing. If overload continues, taking the newest available job first (LIFO) can let some jobs finish while they are still useful.

Older jobs wait longer as a result. LIFO does not create capacity, and old jobs can wait indefinitely unless we proactively remove them when they expire. It is unsuitable when jobs must be processed in order or when every accepted job must eventually finish.

With different kinds of work, FIFO can also leave an urgent alert behind a batch of low-value jobs. Strict priority protects the alert but can starve everything else. We have to decide whether the next slot should favor a deadline, *value per unit of scarce work*, or a guaranteed share for each class. Those goals can conflict.

Scheduling chooses among jobs already waiting. It can keep an urgent alert from sitting behind low-value work, but it cannot reclaim a slot already occupied by a long-running job. Admission also has to decide which work should enter in the first place.

## Preserve slack with probabilistic load shedding

Earlier, \(\mu-\lambda\) was the slack left after admitted work. I want some of that margin available when important traffic spikes, rather than filling every slot with ordinary work first. For a simplified, equal-cost workload, suppose a service can finish 100 jobs/s. It normally admits 60 history-enrichment jobs and 20 alerts each second, leaving 20/s of slack. If enrichment traffic rises to 100/s and we accept all of it, the combined 120 jobs/s exceeds capacity by 20/s. A backlog grows before any new alert spike arrives.

Instead, we can reject each enrichment job with a probability that rises as offered load and resource pressure grow. At 100 enrichment arrivals/s, a 40% drop probability admits about 60/s on average. Together with the usual 20 alerts/s, that preserves roughly 20/s of slack. It can cover a short rise from 20 to 40 alerts/s without a sustained capacity deficit. This is probabilistic shedding: the fraction refused grows with congestion, rather than flipping from accepting all enrichment work to rejecting all of it at one threshold.

A real-time service can make that choice at its entrance and reject cheaply. A pipeline can refuse lower-value work before publishing it, or discard it before an expensive consumer stage, *if the contract allows that work to be lost*. If every job must eventually run, leaving it in the broker is deferral, not shedding; the capacity deficit remains.

The probability expresses a preference; it does not provide a hard safety limit. Random variation and sudden jumps in offered load can still admit too much in a short interval, so the hard limits on active work and local waiting remain necessary. If alerts need a guaranteed share of capacity, we must reserve it or enforce that share through scheduling. I would judge the policy by useful completions and deadline misses for each class during a burst, not by the percentage rejected alone.

## When autoscaling fails

The admission boundary also needs to hold when capacity changes. Return to System A. Suppose a pod becomes so overwhelmed that it misses a health check. If its readiness check fails, Kubernetes stops routing normal traffic to it; if its liveness check fails, Kubernetes restarts it. The remaining pods take more traffic, slow down, and may miss their own checks. Effective capacity falls at exactly the moment the service needs it most.[^kubernetes]

```text
pod stops making progress
→ fewer effective pods
→ more traffic per surviving pod
→ more waiting and failures
→ still fewer effective pods
```

That is why a busy pod should still be able to answer a cheap health check. If it is finishing admitted work but cannot accept more, restarting it only removes useful capacity. Kubernetes cautions that badly designed liveness probes can cause cascading failures.[^kubernetes]

Scaling up can help only after new pods start, become ready, and begin doing useful work. If each new pod accepts requests without bounding its own waiting or checking whether they can still finish, adding replicas may create more places for work to pile up without adding many useful completions. The autoscaler is a control loop with a delay, so we cannot count on additional capacity appearing immediately.[^kubernetes]

In a service that controls admission, losing a pod looks different. Total successes may fall until replacement capacity arrives. Rejections rise. Surviving pods continue to finish admitted work, so the deployment retains a stable base from which to recover. **Overload alone does not mean a service is unhealthy**. A service can be unable to accept another request while still being healthy enough to serve the work it has already accepted.

### Derive the scaling target

The scaling target is where we want to run *before* a burst, not the highest utilization a pod survived in a load test. For our four-core service, that tested limit was 85% CPU while meeting the latency objective. Running at 85% in normal traffic leaves no room for arrivals while new pods start.

Suppose traffic can rise 30% before another pod is ready, with roughly the same request mix. If we start at 65% CPU, that rise takes the existing pods to about 85%: `0.65 × 1.3 ≈ 0.85`. Starting at 85% would push them beyond the tested limit. More generally, a first estimate is:

\[
\rho_{\text{target}} \leq \frac{\rho_{\max}}{B}
\]

Here \(\rho_{\text{target}}\) is utilization before the burst, \(\rho_{\max}\) is the highest utilization that met the latency objective in testing, and \(B\) is the expected traffic multiplier during the scaling delay—1.3 for a 30% rise. Both the safe limit and the burst estimate need to come from measurements, not a generic CPU target.

At 20 milliseconds of CPU per request, 65% of four cores is enough for about 130 useful requests/s per pod. Ten pods could therefore serve 1,300/s before the burst. A 30% rise brings demand to 1,690/s, just under their combined tested limit of 1,700/s. But this leaves no room for a pod failure: nine pods can finish only about 1,530/s at that limit. If the burst and a pod loss can happen together, we need more reserve or a lower target. Admission still has to protect the surviving pods while replacement capacity arrives.

If I use the Kubernetes Horizontal Pod Autoscaler (HPA), I would check the denominator before copying that 65% into `averageUtilization`: HPA measures CPU against the pod's **CPU request**, not the four usable cores assumed here.[^kubernetes]

Admission changes the scaling signal too. Suppose shedding holds each pod near that target while eligible requests are being refused. A CPU-only autoscaler sees no reason to add pods, even though demand is unserved. I would also track unique eligible work that was rejected, or the age of useful backlog in a pipeline, and use an appropriate demand-based scaling signal if more replicas can actually increase the limiting resource. Raw retry attempts and quota denials are not that signal.

Then repeat the calculation for a node or availability zone loss. How much capacity remains, and can the surviving pods reject excess work without collapsing? Scaling policy and per-pod self-defense answer different parts of that question. A load test at 2× or 10× offered traffic is often more revealing than a clean autoscaling graph from a normal afternoon.

## Putting everything together

I would start with three questions before choosing a mechanism:

> How much useful work can finish on time for this workload? Where does the excess go? What does each attempt cost across the whole path?

A CPU graph or a count of broker records does not answer those questions on its own.

At each scarce stage, admission control decides whether work starts, waits within a bound, or is refused or deferred. Quotas, often enforced by rate limiters, allocate shares, not capacity. Probabilistic shedding can refuse a growing fraction of lower-value work as congestion rises, preserving slack for important work. Neither removes the need for hard limits on started work and local waiting. Deadlines and circuit breakers help us avoid work unlikely to finish; a breaker should turn away requests before we spend heavily on preparation for a required downstream call that is already likely to fail. Scheduling chooses which waiting job gets the next slot.

One pod refusing work is defending itself; it is not declaring the entire dependency down. A caller may try another pod while it has time left before its deadline and a remaining retry budget. Repeated refusals across pods suggest that the dependency as a whole has no room, so more attempts are unlikely to help. Each component can make that judgment from its own limits and recent outcomes, but the retry bounds keep those local decisions from becoming a fleet-wide retry storm.

If a request is rejected, a client may retry it; if a consumer pauses, the broker retains it. Neither makes the excess disappear. Even an autoscaler adds capacity only after a delay, and only if the resource that limits throughput actually grows.

### A real-time request service

Suppose a four-core service spends 20 milliseconds of CPU per request, and load testing shows that it completes about 170 useful requests/s within the latency objective for its usual workload mix. It normally receives 130/s, but traffic rises to 200/s for ten seconds. For this sizing example, we also assume workers keep taking about 170 requests/s from the waiting queue during the burst. Accepting the whole spike would then leave roughly 300 requests waiting: 30 excess arrivals/s for ten seconds.

Now compare that backlog with the latency budget. A 100-millisecond queue-wait budget suggests only about 17 waiting places (`170/s × 0.1s`); we might start with 16 and test. That queue can smooth a short burst, but it cannot hold all 300 requests. We also need a separate, load-tested limit on started requests, including those waiting on I/O.

At the HTTP entrance, make the cheap decisions first. A tenant may be out of quota even when the pod has room. A required dependency's breaker may be open even when the tenant has quota. A deadline may already have expired. Lower-value work may be probabilistically shed as congestion grows, preserving slack for more important traffic. If the request can still produce a useful result, try an active slot or a place in the bounded queue. If neither is available, refuse it promptly. Keep the reasons distinct—quota, no viable path, deadline, or capacity—so the caller knows whether another attempt might help.

The queue also needs a rule for who starts next. FIFO may be enough for one class of requests; different deadlines or tenant guarantees may call for another scheduling policy. Discard a request that expires while waiting, and recheck its deadline and required dependency before it starts. A free slot is not a reason to begin work that can no longer produce a useful reply.

```goat
caller (deadline + retry budget)
   |
   v
quota / time / breaker / shed -> reject or degrade
   |
   v
slot or short wait ---------> reject: full / too late
   |
   v
CPU -> limited dependency -> reply -> release slot
```

The active slot stays held through CPU work and I/O, and is released when the work it counts actually stops. If the last dependency slows, upstream services may also retain request contexts in memory while they wait for it. If CPU and I/O use separate worker pools, we also need limits on their handoff queues and on requests returning from I/O to resume processing. Calls to a scarce dependency need their own limit and a breaker check at the call site, since its state may change after admission. Cancellation should reach queued and active work, but a timed-out request is not proof that its computation has stopped; releasing its permit early could put new work beside the old work and exceed the limit.[^cancellation] An unbounded number of coroutines waiting to enter the queue would defeat the boundary we just built.

If the caller retries a quick refusal, the waiting moves there. It may still hold the original request in memory throughout backoff, so a cheap rejection for this pod is not necessarily cheap for the whole path. Keep that retry loop within a deadline and attempt budget, jitter its waits, and honor `Retry-After` when supplied. If a later failure can make the caller repeat expensive preparation, consider caching that result or retrying only the failed step; an unknown outcome also needs an idempotency rule.

Meanwhile, the pod keeps the same admission limits as replicas arrive or disappear. I would graph unique requests offered, retry attempts, admissions, queue wait, rejections by reason, and useful on-time completions together. More pods help only after they are ready; they do not justify unbounded waiting until then.

### A broker-fed data pipeline

Publishing to Kafka or SQS does not mean a job has been admitted to the processing stage whose resources are limited. At the producer, decide whether the job has a deadline, may be discarded, or must eventually run. Give it a logical id so retries can be distinguished from new demand. Quotas can allocate producer shares; lower-value work can be shed before publishing only if its contract permits loss. If every job must run, the producer needs backpressure or a backlog recovery target with enough capacity to meet it.

The consumer limits how many records it fetches and how many jobs it starts. Before expensive processing, discard expired jobs and already-completed duplicates. Scheduling then matters: FIFO may be required for ordered work, while independent expiring jobs may benefit from deadline or value-based ordering. LIFO can save some fresh jobs only when reordering is allowed and old jobs are actively discarded. An open breaker or a full CPU, database, or GPU stage is a reason to defer or discard work according to its contract, not to build another unlimited queue inside the consumer.

```goat
producer (class + deadline + id)
   |
   v
broker backlog
   |
   v
bounded fetch / schedule
   |
   v
cheap check -------> stale / duplicate: mark done
   |
   v
scarce permit -----> no room: defer intake
   |
   v
work --> durable output --> mark input done
```

If no permit is available, leave work in the broker or in a small bounded fetched set. When a costly stage succeeds, make its output durable before marking the input done, with idempotency to handle a crash between those steps. A later stage can then retry without repeating all the preparation; a cache, saved intermediate result, or checkpoint may serve the same purpose. The exact acknowledgement or offset rules depend on the broker and any ordering guarantee.[^broker-admission]

This protects workers but does not by itself control how old the backlog becomes. Watch new logical jobs, retry records, the age of the oldest *useful* job, wasted scarce work, and on-time completions separately. If the expected wait exceeds a job's useful lifetime, the producer side needs backpressure or shedding where the contract permits. Adding consumers will not help if the limiting CPU, database, or GPU capacity has not grown.

In both designs, we should be able to account for every request or job: it runs now, waits in a queue with a size or age limit, returns to its caller for bounded retries, or is discarded when it is no longer useful. Under excess load, useful completions should hold near tested capacity, while successful latency and local resource use stay bounded. The excess should appear as quick rejections or backlog with a known age, not as a collapse in useful throughput. If we cannot explain where the work goes, we have probably hidden another queue rather than controlled overload.

## Revisit the two systems

Returning to the two systems from the beginning, both were offered more work than they could finish. I would put offered requests, attempts, admissions, useful completions, and waiting work on the same timeline for each.

For System A, we know throughput collapsed as pods restarted under the peak. If admissions or hidden waiting continued to grow while useful completions fell, that would explain why adding pods alone did not restore progress. I would check whether retries multiplied attempts, whether expired work still consumed resources, and whether liveness or readiness failures removed capacity before claiming any one cause. Stopping traffic and bringing it back gradually was consistent with getting admitted work back below the rate the service could finish, so the backlog finally had room to drain.

System B had a different shape: admitted work and waiting stayed bounded while quick rejections took the excess. Successful latency remained within the objective and new pods could join without disrupting the existing ones. CPU near 99% was not the measure of success by itself; useful completions, a bounded internal workload, and the fraction of unique offered work finished on time tell us much more.

## A self-defense checklist

Before the next peak, I would want short answers to four questions:

- What resource limits useful completions for each important kind of request, and what does one attempt cost there?
- Where can work wait—at admission, in a worker handoff, at a dependency, in a broker, or at a caller—and what bounds its number and age?
- Can we refuse work that is over quota, too late, or unlikely to succeed *before* it consumes that resource? If work is cancelled, when is the resource actually free?
- Under excess traffic or a slow dependency, do useful completions hold up, local waiting and memory remain bounded, and eligible rejections remain visible?

During an incident, I would compare unique offered work, retry attempts, admissions, useful on-time completions, and the age of the oldest useful backlog. Then I would adjust the limit that is failing and watch for evidence that the change helped:

- If admitted and in-flight work grow while useful completions fall, limit new starts at the scarce stage. Check whether useful throughput recovers as waiting and memory stabilize.
- If expired work or costly retries occupy that stage, discard stale work or refuse doomed attempts earlier. Wasted resource time should fall, not just the attempt count.
- If completions and latency hold steady while eligible rejections rise, self-defense is working but demand is still unmet. Add capacity at the *actual* bottleneck if that demand should be served, then check that useful completions rise and rejections fall.

Queues, retries, circuit breakers, and autoscalers are not answers by themselves. They move waiting, stop attempts, or add capacity after a delay. I want to trace a request through the whole path and account for each step: CPU, memory, active slots, connections, downstream work, and the cost of giving up. When the last dependency slows, which upstream requests stay in memory? If we retry, which work repeats and what remains allocated during backoff? Only then can we decide which boundary to add and where.

The question I would take to a design review is: **if callers send ten times as many requests as the service can handle tomorrow, or a required dependency slows tenfold, what will keep completing on time, and where will the rest of the work go?** I do not want every caller to know how to keep my service alive. I want the service to limit its load according to its capacity and tell callers clearly when it cannot take more, leaving them to decide whether another attempt is worth its cost.

[^status]: The service in the opening incident used `429` for overload. [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html) defines `429` for a client that has sent too many requests in a given time. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) defines `503` for temporary server overload or maintenance and permits `Retry-After`. The choice affects client behavior and monitoring, so it should be explicit in the API contract.
[^breaker]: The standard [circuit breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) uses recent failures to skip operations likely to fail, then probes for recovery. The same early decision can protect the calling component's own threads, connections, memory, and CPU time.
[^retries]: See Google's [handling overload](https://sre.google/sre-book/handling-overload/) for retry budgets and behavior under widespread overload, AWS on [backoff with jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), and AWS on [idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
[^stage-retry]: [SQS standard queues can deliver a message more than once](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html). [Kafka transactions](https://kafka.apache.org/design/) can coordinate output records with consumed offsets. [Flink checkpoints](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/) restore managed state, but recovery replays input after the last checkpoint; end-to-end exactly-once effects also require a transactional or idempotent sink.
[^broker-admission]: Kafka consumers can [pause fetching and commit processed offsets](https://kafka.apache.org/42/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html). An [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) makes received messages temporarily invisible; consumers delete them after processing, or they become visible again if not deleted before the timeout.
[^kubernetes]: Kubernetes documents the timing of [horizontal pod autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) and the different effects of [liveness and readiness probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/).
[^tokio]: Tokio's [`Sender::send` documentation](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html) says it waits for channel capacity, while [`try_send`](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html#method.try_send) returns immediately if the buffer is full.
[^cancellation]: Tokio documents that a running [`spawn_blocking` task cannot be aborted](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html). The permit for such work must remain held until the work actually exits, even if the request that started it has already timed out.

<!-- Before publication, verify the opening incident figures and the author's personal role in System B against the original operational notes. The opening uses the author's Kubernetes and HTTP-status details. -->
