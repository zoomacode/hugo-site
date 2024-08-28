import random
import matplotlib.pyplot as plt
from tabulate import tabulate


class RandomCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = set()

    def contains(self, request: int) -> bool:
        return request in self.cache

    def add(self, request: int):
        if len(self.cache) == self.capacity:
            random_choice = random.choice(list(self.cache))
            self.cache.remove(random_choice)
        self.cache.add(request)


class LruCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = set()

    def contains(self, request: int) -> bool:
        res = request in self.cache
        if res:
            self.cache.remove(request)
            self.cache.add(request)

        return res

    def add(self, request: int):
        if len(self.cache) == self.capacity:
            self.cache.pop()
        self.cache.add(request)


class PNcCache:
    def __init__(self, capacity: int, num_choices: int):
        self.capacity = capacity
        self.cache = dict()
        self.num_choices = num_choices
        self.counter = 0

    def contains(self, request: int) -> bool:
        res = request in self.cache
        if res:
            self.cache[request] = self.counter
            self.counter += 1
        return res

    def add(self, request: int):
        if len(self.cache) == self.capacity:
            choices = list(self.cache.keys())
            choices = list(random.choices(choices, k=self.num_choices))
            to_evict = min(choices, key=self.cache.get)
            del self.cache[to_evict]

        self.cache[request] = self.counter
        self.counter += 1


def generate_queryset(n: int) -> list[int]:
    return [i for i in range(n)]


def generate_query_weights(n: int) -> list[float]:
    """
    Generates a list of query weights
    more weight means more likely to be selected
    lower number have higher weights
    weights follow gamma distribution density
    """

    weights = sorted([random.gammavariate(2, 0.5) for _ in range(n)])
    total = sum(weights)
    return [total / w for w in weights]


import matplotlib.pyplot as plt

images_suffix = "latency"


def plot_weights_histogram(weights: list[float]):
    """
    Plot the histogram of the weights.

    Args:
        weights (list[float]): List of weights.
    """
    plt.figure(figsize=(10, 6))  # Set the figure size to 1000x600 pixels
    plt.hist(weights, bins=100, density=True, histtype="step", color="blue")
    plt.xlabel("Weights")
    plt.ylabel("Frequency")
    plt.title("Query Weights Distribution")
    plt.savefig(
        f"images/query-weights-distribution-{images_suffix}.png", dpi=100
    )  # Set the dpi to adjust the image resolution


def print_distribution_of_query_ids(requests: list[int]):
    plt.figure(figsize=(10, 6))  # Set the figure size to 1000x600 pixels
    plt.hist(
        requests, bins=100, cumulative=True, histtype="step", color="blue", density=True
    )
    plt.xlabel("Query IDs")
    plt.ylabel("Frequency")
    plt.title("Query IDs Distribution")
    plt.savefig(f"images/query-ids-distribution-{images_suffix}.png")


def run_experiment(requests: list[int], cache, warmup=0.1):
    warmup_size = int(len(requests) * warmup)
    for request in requests[:warmup_size]:
        cache.add(request)

    use_requests = requests[:warmup_size]
    hits = 0
    misses = 0
    for request in use_requests:
        if cache.contains(request):
            hits += 1
        else:
            misses += 1
            cache.add(request)
    return hits / len(use_requests) * 100.0, misses / len(use_requests) * 100.0


def main():
    random.seed(42)
    number_of_queries = 100000
    number_of_requests = number_of_queries * 10
    queries = generate_queryset(number_of_queries)
    weights = generate_query_weights(number_of_queries)
    plot_weights_histogram(weights)

    requests = random.choices(queries, weights=weights, k=number_of_requests)

    print_distribution_of_query_ids(requests)
    print("Number of queries:", len(queries))
    print("Number of requests:", len(requests))
    print("Number of unique requests:", len(set(requests)))
    # first 100 requests
    print("First 100 requests:", requests[:100])

    results = []

    # uniform cache sizes from 0.05 to 0.20 with 0.02 step
    for c in range(1, 21, 1):
        print("Running experiment for cache size:", c)
        cache_size = int(c / 100 * number_of_queries)
        random_hits, _ = run_experiment(requests, RandomCache(cache_size))
        lru_hits, _ = run_experiment(requests, LruCache(cache_size))
        p2c_hits, _ = run_experiment(requests, PNcCache(cache_size, 2))
        p3c_hits, _ = run_experiment(requests, PNcCache(cache_size, 3))
        print("Results:", random_hits, lru_hits, p2c_hits, p3c_hits)

        results.append((c, random_hits, lru_hits, p2c_hits, p3c_hits))

    # print results using tabulate
    print(
        tabulate(
            results,
            headers=["Cache Size", "Random", "LRU", "P2C", "P3C"],
            tablefmt="github",
        )
    )
    # draw results
    plt.figure(figsize=(10, 6))  # Set the figure size to 1000x600 pixels
    plt.plot([r[0] for r in results], [r[1] for r in results], label="Random")
    plt.plot([r[0] for r in results], [r[2] for r in results], label="LRU")
    plt.plot([r[0] for r in results], [r[3] for r in results], label="P2C")
    plt.plot([r[0] for r in results], [r[4] for r in results], label="P3C")

    # save the plot
    plt.legend()
    plt.xlabel("Cache Size (%)")
    plt.ylabel("Hit Rate (%)")
    plt.title("Cache Eviction Policies")
    plt.savefig(f"images/cache-eviction-lru-and-p2c-{images_suffix}.png")


if __name__ == "__main__":
    main()
