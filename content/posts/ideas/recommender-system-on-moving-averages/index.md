---
title: "Recommender System on HNSW and Exponential Moving Averages"
date: 2024-10-11T21:29:10-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
    - Algorithms
---

#### Intro

I was reading the original paper on "Hierarchical Navigable Small Worlds (HNSW)" https://arxiv.org/abs/1603.09320 which I found much easier to understand than all those YouTube videos I tried to watch and articles to read. Back to the topic, HNSW is a probabilistic data structure for searching neighbors in multi-dimensional space.
One of practical applications is search of semantically close objects. Reading that paper and some other activities made me curious if I can quickly implement a recommendation system which combines three things: HNSW, moving averages, and randomness.

One more challenge I want to add is not to use any tutorials and try to pull everything together using the knowledge I have, except for the documentation for libraries.

#### Recommendation system

I didn't want to spend to much time on it so I decided to use a simple of the shelf components but not too complex too leave room for learning. The main ideas were:

1. an exponential moving average across selected by the user results should work just fine as a way to build a user recommendations profile.
1. by adding noise to the user profile, we can implement an exploration mode almost for free.

**The ingredients**:

1. [Ollama](https://ollama.com) + `nomic-embed-text`
1. [Faiss](https://faiss.ai) for HNSW
1. [A movies dataset from Cohere](https://huggingface.co/datasets/Cohere/movies) - was found by something like "embeddings dataset" in Google.
1. Numpy, Pandas etc to

**The algorithm**:

-   Download dataset
-   Generate embeddings

```python
def apply_embedings(row):
    prompt = str(row.to_dict())
    emb = ollama.embeddings(
        model="nomic-embed-text",
        # model="snowflake-arctic-embed",
        prompt=prompt,
    )
    # print(prompt, emb)
    return emb["embedding"]
```

-   Build HNSW index

```python
    raw_embs = np.zeros((len(embs), len(embs["embedding"].values[0])), dtype=np.float32)
    for i, (_, row) in enumerate(embs.iterrows()):
        raw_embs[i] = row["embedding"]

    dimension = raw_embs.shape[1]
    data_size = raw_embs.shape[0]

    index = faiss.IndexHNSWFlat(dimension, data_size)
    index.add(raw_embs)
```

-   Use average across all embeddings as initial user profile
-   Compute embedding for a search request
-   Search and give the user an option to select a movie
-   Update the user profile by the embeddings from the selected movie using EMA.
-   Repeat

Documentation for Faiss library was the hardest part. The rest was pretty straight forward especially with Copilot enabled.

#### Testing

The system [code](./src/generate_embedings.py) will ask for a search request and the return search results + recommendations from the previous iteration. It is done this way just because I don't want to spend to much time on making it nicer.

**Attempt number one**: we enter search request `hackers`. The search results are good and we get some default recommendations since the user profile was not updated yet + two sets of recommendations with added noise.

```
Welcome to the movie recommender system

Type 'exit' to quit
Enter a movie title: hackers
+--------------------------+----------------------------+
| Recommendations:         | Recommendations (noise):   |
| 1. Role Models           | 1. Small Apartments        |
| 2. Practical Magic       | 2. Hall Pass               |
| 3. Bringing Out the Dead | 3. Dysfunctional Friends   |
| 4. The Fisher King       | 4. The Chumscrubber        |
| 5. Kiss of Death         | 5. The Exploding Girl      |
+--------------------------+----------------------------+
| Search results:          | Recommendations (buckets): |
| 1. Hackers               | 1. Practical Magic         |
| 2. Gamer                 | 2. Role Models             |
| 3. Antitrust             | 3. The Adjustment Bureau   |
| 4. Micmacs               | 4. Secondhand Lions        |
| 5. Mindhunters           | 5. The Informers           |
+--------------------------+----------------------------+
Pick one of the movies from the search results to update your preferences
Enter a movie number: 5
You selected:
Mindhunters
```

**Second attempt**: we entered `pricess yolo` I have no clue if results have anything to do with the request but we see that recommendation now have `Mindhunters` we selected in the end of previous iteration.

```
Welcome to the movie recommender system

Type 'exit' to quit
Enter a movie title: pricess yolo
+------------------------------------+---------------------------------------------+
| Recommendations:                   | Recommendations (noise):                    |
| 1. Mindhunters                     | 1. Abduction                                |
| 2. Role Models                     | 2. Justin Bieber: Never Say Never           |
| 3. The Death and Life of Bobby Z   | 3. The Past Is a Grotesque Animal           |
| 4. Witless Protection              | 4. The Wailing                              |
| 5. Cape Fear                       | 5. Gory Gory Hallelujah                     |
+------------------------------------+---------------------------------------------+
| Search results:                    | Recommendations (buckets):                  |
| 1. The Goods: Live Hard, Sell Hard | 1. It Follows                               |
| 2. Manderlay                       | 2. See Spot Run                             |
| 3. UHF                             | 3. Cirque du Freak: The Vampire's Assistant |
| 4. Trading Places                  | 4. The Mask                                 |
| 5. Who's Your Caddy?               | 5. Role Models                              |
+------------------------------------+---------------------------------------------+
Pick one of the movies from the search results to update your preferences
Enter a movie number: 2
You selected:
Manderlay
```

**Attempt number three**: we continue to see that search works + recommendations based on EMA of embeddings works just fine. Also bucket level noise seems to give results closed to the original recommendations.

```
Welcome to the movie recommender system

Type 'exit' to quit
Enter a movie title: die hard
+-------------------------------+---------------------------------------------+
| Recommendations:              | Recommendations (noise):                    |
| 1. Manderlay                  | 1. Run All Night                            |
| 2. Mindhunters                | 2. Taxman                                   |
| 3. Cape Fear                  | 3. Cavite                                   |
| 4. Role Models                | 4. Light Sleeper                            |
| 5. The Adjustment Bureau      | 5. 16 Blocks                                |
+-------------------------------+---------------------------------------------+
| Search results:               | Recommendations (buckets):                  |
| 1. Die Hard                   | 1. Manderlay                                |
| 2. Die Hard: With a Vengeance | 2. Blood Diamond                            |
| 3. Die Hard 2                 | 3. City of Angels                           |
| 4. Live Free or Die Hard      | 4. Cirque du Freak: The Vampire's Assistant |
| 5. A Good Day to Die Hard     | 5. A.I. Artificial Intelligence             |
+-------------------------------+---------------------------------------------+
Pick one of the movies from the search results to update your preferences
Enter a movie number: 4
You selected:
Live Free or Die Hard
```

**The last attempt**: the pattern remains.

```
Welcome to the movie recommender system

Type 'exit' to quit
Enter a movie title: show
+----------------------------------+----------------------------+
| Recommendations:                 | Recommendations (noise):   |
| 1. Live Free or Die Hard         | 1. Eagle Eye               |
| 2. Mindhunters                   | 2. Getaway                 |
| 3. Witless Protection            | 3. Road House              |
| 4. The Death and Life of Bobby Z | 4. Rat Race                |
| 5. The Adjustment Bureau         | 5. Ishtar                  |
+----------------------------------+----------------------------+
| Search results:                  | Recommendations (buckets): |
| 1. Best in Show                  | 1. Bringing Out the Dead   |
| 2. UHF                           | 2. Confidence              |
| 3. The Original Kings of Comedy  | 3. The Family Man          |
| 4. The Greatest Show on Earth    | 4. Law Abiding Citizen     |
| 5. Certifiably Jonathan          | 5. Manderlay               |
+----------------------------------+----------------------------+
```

### Conclusion

The theory that we can use EMA as a way to build user based recommendation without storing history of searches is confirmed.
In addition to that, a bucket based randomness seems to be a good exploration mechanism.
