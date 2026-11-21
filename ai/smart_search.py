
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@lru_cache(maxsize=32)
def get_book_embeddings(book_texts):
    return model.encode(
        list(book_texts),
        convert_to_tensor=True
    )


def semantic_search(query, books, top_k=5):

    if not query or not books:
        return []

    book_texts = []

    for book in books:
        text = (
            str(book.get("Title") or "") + " " +
            str(book.get("Author") or "") + " " +
            str(book.get("Category") or "") + " " +
            str(book.get("Description") or "")
        )

        book_texts.append(text)

    # Reuse cached embeddings when book data has not changed
    book_embeddings = get_book_embeddings(tuple(book_texts))

    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        query_embedding,
        book_embeddings
    )[0]

    results = []

    for index, score in enumerate(scores):
        book = books[index].copy()

        book["search_similarity"] = round(
            float(score) * 100,
            2
        )

        results.append(book)

    results.sort(
        key=lambda item: item["search_similarity"],
        reverse=True
    )

    filtered_results = [
        book for book in results
        if book["search_similarity"] >= 30
    ]

    return filtered_results[:top_k]
