import pandas as pd
import numpy as np
import random
import ollama
import os
from tqdm import tqdm
import faiss
from tabulate import tabulate


def apply_embedings(row):
    prompt = str(row.to_dict())
    emb = ollama.embeddings(
        model="nomic-embed-text",
        # model="snowflake-arctic-embed",
        prompt=prompt,
    )
    # print(prompt, emb)
    return emb["embedding"]


def get_emdeddings() -> pd.DataFrame:
    if os.path.exists("movies_embeddings.parquet"):
        return pd.read_parquet("movies_embeddings.parquet")

    # Load the movies dataset
    if os.path.exists("movies.parquet"):
        df = pd.read_parquet("movies.parquet")
    else:
        df = pd.read_parquet("hf://datasets/Cohere/movies/movies.parquet")
        df.to_parquet("movies.parquet")

    # print(df.columns)
    # print(df.head())

    # Apply the embedings with progress bar
    tqdm.pandas()
    df["embedding"] = df.progress_apply(apply_embedings, axis=1)

    # Save the embeddings
    df.to_parquet("movies_embeddings.parquet")
    return df


def get_index(embs: pd.DataFrame) -> tuple[faiss.Index, np.array, np.array, np.array]:
    if os.path.exists("movies.index"):
        return (
            faiss.read_index("movies.index"),
            np.fromfile("average_embedding.bin", dtype=np.float32),
            np.fromfile("min_embedding.bin", dtype=np.float32),
            np.fromfile("max_embedding.bin", dtype=np.float32),
        )

    raw_embs = np.zeros((len(embs), len(embs["embedding"].values[0])), dtype=np.float32)
    for i, (_, row) in enumerate(embs.iterrows()):
        raw_embs[i] = row["embedding"]

    dimension = raw_embs.shape[1]
    data_size = raw_embs.shape[0]

    index = faiss.IndexHNSWFlat(dimension, data_size)
    index.add(raw_embs)

    # sanity check
    # D, I = index.search(raw_embs[:5], 5)
    # print(I)
    # print(D)
    # print(embs.iloc[I[0]])

    # save average, min, and max embedding
    avg_emb = raw_embs.mean(axis=0)
    min_emb = raw_embs.min(axis=0)
    max_emb = raw_embs.max(axis=0)
    avg_emb.tofile("average_embedding.bin")
    min_emb.tofile("min_embedding.bin")
    max_emb.tofile("max_embedding.bin")

    faiss.write_index(index, "movies.index")
    return index, avg_emb, min_emb, max_emb


def search(index, query: str, top_k: int = 5):
    emb = apply_embedings(pd.Series({"title": query}))
    D, I = index.search(np.array([emb]), top_k)
    return D, I


def get_recommenations(raw_emb: np.array, index, top_k: int = 5):
    D, I = index.search(np.array([raw_emb]), top_k)
    return D, I


def update_avg_embeddings(pre_emb: np.array, new_emb: np.array, n: int = 8):
    return (pre_emb * n + new_emb) / (n + 1)


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


def print_recommenations(title, embs: pd.DataFrame, I: np.array):
    result = f"{title}\n"
    for i in range(len(I[0])):
        title = embs.iloc[I[0][i]]["title"]
        result += f"{i + 1}. {title}\n"
    result += "\n"
    return result


if __name__ == "__main__":
    embs = get_emdeddings()
    index, avg_emb, min_emb, max_emb = get_index(embs)
    random_noise_emb = randmoize_embedding(avg_emb)
    random_bucket_emb = randomize_embedding_with_min_max(avg_emb, min_emb, max_emb)
    if os.path.exists("user.bin"):
        user_emb = np.fromfile("user.bin", dtype=np.float32)
    else:
        user_emb = avg_emb.copy()

    n = 5
    while True:
        print("Welcome to the movie recommender system")
        print()
        D, I = get_recommenations(user_emb, index)
        rec_msg = print_recommenations("Recommendations:", embs, I)
        # print(rec_msg)

        D, I = get_recommenations(random_noise_emb, index)
        rec_noise_msg = print_recommenations("Recommendations (noise):", embs, I)
        # print(rec_noise_msg)

        D, I = get_recommenations(random_bucket_emb, index)
        rec_bucket_noise_msg = print_recommenations(
            "Recommendations (buckets):", embs, I
        )
        # print(rec_bucket_noise_msg)

        print("Type 'exit' to quit")
        query = input("Enter a movie title: ")
        if query == "exit":
            break

        D, I = search(index, query, top_k=n)
        search_msg = print_recommenations("Search results:", embs, I)
        # print(search_msg)

        table = [[rec_msg, rec_noise_msg], [search_msg, rec_bucket_noise_msg]]
        print(tabulate(table, tablefmt="grid"))

        print(
            "Pick one of the movies from the search results to update your preferences"
        )
        movie_id = int(input("Enter a movie number: "))

        print("You selected:")
        print(embs.iloc[I[0][int(movie_id - 1)]]["title"])

        user_emb = update_avg_embeddings(
            user_emb, embs.iloc[I[0][int(movie_id - 1)]]["embedding"], n
        )
        random_noise_emb = randmoize_embedding(user_emb)
        random_bucket_emb = randomize_embedding_with_min_max(user_emb, min_emb, max_emb)

        # save the user embedding
        user_emb.tofile("user.bin")
