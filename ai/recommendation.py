from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendations(selected_book, books, limit=3):

    if not books:
        return []

    selected_id = selected_book["Book_ID"]

    all_books = [
        book for book in books
        if book["Book_ID"] != selected_id
    ]

    if not all_books:
        return []

    documents = []

    for book in [selected_book] + all_books:
        text = " ".join([
            str(book.get("Title", "")),
            str(book.get("Author", "")),
            str(book.get("Category", "")),
            str(book.get("Description", ""))
        ])
        documents.append(text)

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    results = []

    for index, score in enumerate(similarities):

        book = all_books[index].copy()

        book["similarity"] = round(
            float(score) * 100, 2
        )

        results.append(book)

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:limit]