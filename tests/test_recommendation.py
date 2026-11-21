
from ai.recommendation import get_recommendations


books = [
    {
        "Book_ID": 1,
        "Title": "Python Programming",
        "Author": "John Smith",
        "Category": "Programming",
        "Description": "Learn Python programming"
    },
    {
        "Book_ID": 2,
        "Title": "Advanced Python",
        "Author": "Ahmed Ali",
        "Category": "Programming",
        "Description": "Advanced Python coding"
    },
    {
        "Book_ID": 3,
        "Title": "Java Programming",
        "Author": "Michael Brown",
        "Category": "Programming",
        "Description": "Java software development"
    },
    {
        "Book_ID": 4,
        "Title": "Egyptian History",
        "Author": "Ali Hassan",
        "Category": "History",
        "Description": "Ancient Egyptian history"
    }
]


def test_recommendations_not_empty():
    result = get_recommendations(books[0], books)

    assert len(result) > 0


def test_selected_book_not_recommended():
    result = get_recommendations(books[0], books)

    recommended_ids = [
        book["Book_ID"] for book in result
    ]

    assert 1 not in recommended_ids


def test_recommendation_limit():
    result = get_recommendations(
        books[0],
        books,
        limit=2
    )

    assert len(result) <= 2


def test_no_other_books():
    result = get_recommendations(
        books[0],
        [books[0]]
    )

    assert result == []
def test_recommendations_empty_books():
    selected_book = {
        "Book_ID": 1,
        "Title": "Python",
        "Author": "Test Author",
        "Category": "Programming",
        "Description": "Learn Python"
    }

    result = get_recommendations(selected_book, [])

    assert result == []