---
title: "Рекомендательная система на основе HNSW и экспоненциальных скользящих средних"
date: 2024-10-11T21:29:10-07:00
draft: false
author: Anton Golubtsov
summary:
tags:
    - Software Development
    - Algorithms
---

### Введение

Я читал оригинальную статью о "Hierarchical Navigable Small Worlds (HNSW)" https://arxiv.org/abs/1603.09320, которая оказалась гораздо легче для понимания, чем все те видео на YouTube, которые я пытался посмотреть, и статьи, которые читал. HNSW — это вероятностная структура данных для поиска соседей в многомерном пространстве.

Одно из практических применений HNSW — это поиск семантически близких объектов. Прочтение этой статьи и некоторые другие активности заставили меня задуматься, смогу ли я быстро реализовать рекомендательную систему, которая объединяет три вещи: HNSW, скользящие средние и случайность.

Ещё одну задачу, которую я хотел добавить, — это не использовать никакие учебные пособия и попробовать всё собрать, используя только мои знания, за исключением документации для библиотек.

### Рекомендательная система

Я не хотел тратить слишком много времени на проект, поэтому решил использовать простые готовые компоненты, но не слишком сложные, чтобы оставить место для обучения. Основные идеи были следующими:

1. Мы можем использовать экспоненциальное скользящее среднее по выбранным пользователем результатам как способ построения профиля пользователя для рекомендаций.
2. Добавив шум в пользовательский профиль, можно почти бесплатно реализовать режим исследования.

Для создания рекомендательной системы я решил использовать следующие компоненты:

1. [Набор данных фильмов от Cohere](https://huggingface.co/datasets/Cohere/movies) как коллекцию фильмов для выбора.
2. [Ollama](https://ollama.com) + `nomic-embed-text` для генерации эмбеддингов фильмов.
3. [Faiss](https://faiss.ai) для семантического поиска HNSW.

Весь процесс достаточно простой:

Сначала мы загружаем набор данных:

```python
df = pd.read_parquet("hf://datasets/Cohere/movies/movies.parquet")
```

Затем мы генерируем эмбеддинги с использованием Ollama и модели `nomic-embed-text`.

```python
def apply_embedings(row):
    prompt = str(row.to_dict())
    emb = ollama.embeddings(
        model="nomic-embed-text",
        prompt=prompt,
    )
    return emb["embedding"]

tqdm.pandas()
df["embedding"] = df.progress_apply(apply_embedings, axis=1)
```

На основе эмбеддингов мы строим индекс HNSW и начальный профиль пользователя:

```python
    # building input for the index which requires a continues piece of memory
    # so numpy comes in handy.
    raw_embs = np.zeros((len(embs), len(embs["embedding"].values[0])), dtype=np.float32)
    for i, (_, row) in enumerate(embs.iterrows()):
        raw_embs[i] = row["embedding"]

    # building index
    dimension = raw_embs.shape[1]
    data_size = raw_embs.shape[0]
    index = faiss.IndexHNSWFlat(dimension, data_size)
    index.add(raw_embs)

    # preparing data for building a user profile
    avg_emb = raw_embs.mean(axis=0)
    min_emb = raw_embs.min(axis=0)
    max_emb = raw_embs.max(axis=0)
    avg_emb.tofile("average_embedding.bin")
    min_emb.tofile("min_embedding.bin")
    max_emb.tofile("max_embedding.bin")

    faiss.write_index(index, "movies.index")
```

Реализация логики поиска достаточно проста:

```python
def search(index, query: str, top_k: int = 5):
    emb = apply_embedings(pd.Series({"title": query}))
    D, I = index.search(np.array([emb]), top_k)
    return D, I
```

Затем мы просим пользователя выбрать один из фильмов и обновляем профиль пользователя, применяя EMA к каждому эмбеддингу:

```python
def update_avg_embeddings(pre_emb: np.array, new_emb: np.array, n: int = 8):
    return (pre_emb * n + new_emb) / (n + 1)
....
....
user_emb = update_avg_embeddings(
            user_emb, embs.iloc[I[0][int(movie_id - 1)]]["embedding"], n
        )
```

Для генерации рекомендаций мы используем ту же логику, что и для поиска, но в качестве поискового запроса используем профиль пользователя:

```python
def get_recommenations(raw_emb: np.array, index, top_k: int = 5):
    D, I = index.search(np.array([raw_emb]), top_k)
    return D, I


D, I = get_recommenations(user_emb, index)
```

Для исследовательских рекомендаций мы используем тот же профиль пользователя, но с добавленным шумом:

```python
def randmoize_embedding(emb: np.array, percent_of_change: float = 0.25):
    noise = np.random.normal(1, 1 + percent_of_change, emb.shape)
    negative = random.choice([True, False])
    if negative:
        noise = -noise

    return emb + noise


def randomize_embedding_with_min_max(
    emb: np.array, min_emb: np.array, max_emb: np.array, percent_of_change: float = 0.1
):
    """It selects a percent of buckets in an embedding and randomizes them within the min and max embedding values"""
    new_emb = emb.copy()
    buckets_to_change = random.choices(
        range(emb.shape[0]), k=int(emb.shape[0] * percent_of_change)
    )
    noise = np.random.uniform(min_emb, max_emb, emb.shape)
    new_emb[buckets_to_change] = noise[buckets_to_change]
    return new_emb


random_noise_emb = randmoize_embedding(user_emb)
random_bucket_emb = randomize_embedding_with_min_max(user_emb, min_emb, max_emb)


D, I = get_recommenations(random_noise_emb, index)
rec_noise_msg = print_recommenations("Recommendations (noise):", embs, I)

D, I = get_recommenations(random_bucket_emb, index)
rec_bucket_noise_msg = print_recommenations("Recommendations (buckets):", embs, I)
```

Вот, собственно, и всё.

#### Направления для улучшения

Основной недостаток заключается в том, что мы добавляем выбранный фильм в профиль пользователя, что может привести к генерации рекомендаций, схожих с историей просмотров пользователя.  
Чтобы смягчить эту проблему, я бы попробовал использовать выбранный фильм для поиска фильмов, близких к нему, а затем использовать различные их комбинации. Например:

1. Использовать следующий ближайший фильм.
2. Вычислять среднее значение для ближайших соседей.
3. Использовать взвешенное среднее вместо обычного среднего или, возможно, "Гауссово среднее".

Ещё одна область для экспериментов — это сделать рекомендации более осведомлёнными о времени. Это позволит не показывать пользователю то, что его может больше не интересовать, особенно если он посещает систему редко с большими временными промежутками между посещениями. В таком случае временное затухание может быть лучшим вариантом. См. [Moving Averages]({{< ref "/posts/2024/10/moving-averages" >}} "Moving Averages").

Третье направление — показать пользователю разные типы рекомендаций и посмотреть, что он выберет.

Также можно попробовать различные подходы для добавления элемента исследования.

#### Тестирование

Система [код](./src/generate_embedings.py) запрашивает поисковый запрос и возвращает результаты поиска + рекомендации из предыдущей итерации. Это сделано так просто потому, что я не хочу тратить слишком много времени на создание более красивого решения.

**Первая попытка**: мы вводим поисковый запрос `hackers`. Результаты поиска хорошие, и мы получаем несколько стандартных рекомендаций, так как профиль пользователя ещё не обновлён, плюс два набора рекомендаций с добавленным шумом.

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

**Вторая попытка**: мы ввели `pricess yolo`. Я не уверен, имеют ли результаты какое-то отношение к запросу, но видно, что в рекомендациях теперь есть `Mindhunters`, который мы выбрали в конце предыдущей итерации.

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

**Третья попытка**: мы продолжаем видеть, что поиск работает, а рекомендации на основе EMA эмбеддингов тоже работают хорошо. Кроме того, шум на уровне корзин, похоже, даёт результаты, близкие к исходным рекомендациям.

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

**Последняя попытка**: картина остаётся неизменной.

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

#### Заключение

Теория о том, что мы можем использовать EMA как способ построения пользовательских рекомендаций без хранения истории запросов, подтверждена.  
Кроме того, случайность на уровне корзин кажется хорошим механизмом для исследования.

#### Набор данных

[A movies dataset from Cohere](https://huggingface.co/datasets/Cohere/movies)

![](./src/dataset.png)
