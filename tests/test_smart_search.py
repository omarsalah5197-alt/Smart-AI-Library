
from ai.smart_search import semantic_search

books = [
    {
        "Book_ID": 1,
        "Title": "Python Programming",
        "Author": "John Smith",
        "Category": "Programming",
        "Description": "Learn Python programming and coding"
    },
    {
        "Book_ID": 2,
        "Title": "Advanced Python",
        "Author": "Ahmed Ali",
        "Category": "Programming",
        "Description": "Advanced Python development"
    },
    {
        "Book_ID": 3,
        "Title": "Java Programming",
        "Author": "Michael Brown",
        "Category": "Programming",
        "Description": "Learn Java software development"
    },
    {
        "Book_ID": 4,
        "Title": "Egyptian History",
        "Author": "Ali Hassan",
        "Category": "History",
        "Description": "Ancient Egyptian civilization"
    }
]


def test_search_returns_results():
    result = semantic_search("Python programming", books)
    assert len(result) > 0


def test_empty_query():
    result = semantic_search("", books)
    assert result == []


def test_empty_books():
    result = semantic_search("Python", [])
    assert result == []


def test_results_are_sorted():
    result = semantic_search("Python programming", books)

    scores = [book["search_similarity"] for book in result]

    assert scores == sorted(scores, reverse=True)


def test_search_limit():
    result = semantic_search("Python programming", books, top_k=2)

    assert len(result) <= 2


def test_results_contain_similarity():
    result = semantic_search("Python programming", books)

    for book in result:
        assert "search_similarity" in book
        assert isinstance(book["search_similarity"], float)
