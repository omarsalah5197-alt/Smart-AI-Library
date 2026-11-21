
from ai import smart_assistant as assistant
from unittest.mock import patch
from ai.smart_assistant import (
    detect_intent,
    semantic_detect_intent,
    assistant_response
)

books = [
    {
        "Book_ID": 1,
        "Title": "Python Programming",
        "Author": "John Smith",
        "Category": "Programming",
        "Description": "Learn Python programming",
        "Available_Copies": 3
    },
    {
        "Book_ID": 2,
        "Title": "Advanced Python",
        "Author": "Ahmed Ali",
        "Category": "Programming",
        "Description": "Advanced Python development",
        "Available_Copies": 0
    }
]

borrowings = [
    {
        "Book_Title": "Python Programming",
        "Borrow_Date": "2026-11-20"
    }
]


# Intent Detection Tests

def test_detect_available_books():
    assert assistant.detect_intent("Show available books") == "available_books"


def test_detect_recommendation():
    assert assistant.detect_intent("رشحلي كتب") == "recommendation"


def test_detect_borrowing_status():
    assert assistant.detect_intent("وريني استعاراتي") == "borrowing_status"


def test_detect_book_search():
    assert assistant.detect_intent("عايز كتاب عن البرمجة") == "book_search"


def test_detect_help():
    assert assistant.detect_intent("مساعدة") == "help"


def test_detect_empty_query():
    assert assistant.detect_intent("") == "unknown"


# Assistant Response Tests

def test_available_books_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "available_books"
    )

    result = assistant.assistant_response("Show available books", books)

    assert result["intent"] == "available_books"
    assert len(result["books"]) == 1
    assert result["books"][0]["Book_ID"] == 1


def test_borrowing_status_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "borrowing_status"
    )

    result = assistant.assistant_response(
        "Show my borrowings",
        books,
        borrowings
    )

    assert result["intent"] == "borrowing_status"
    assert len(result["books"]) == 1


def test_help_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "help"
    )

    result = assistant.assistant_response("Help me", books)

    assert result["intent"] == "help"
    assert result["books"] == []
    assert "search for books" in result["message"]


def test_unknown_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "unknown"
    )

    monkeypatch.setattr(
        assistant,
        "detect_intent",
        lambda query: "unknown"
    )

    result = assistant.assistant_response("Random question", books)

    assert result["intent"] == "unknown"
    assert result["books"] == []


def test_book_search_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "book_search"
    )

    monkeypatch.setattr(
        assistant,
        "semantic_search",
        lambda query, books: [books[0]]
    )

    result = assistant.assistant_response("Find Python books", books)

    assert result["intent"] == "book_search"
    assert len(result["books"]) == 1


def test_recommendation_response(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "recommendation"
    )

    monkeypatch.setattr(
        assistant,
        "semantic_search",
        lambda query, books, top_k=5: [books[0]]
    )

    monkeypatch.setattr(
        assistant,
        "get_recommendations",
        lambda selected_book, books, limit=3: [books[1]]
    )

    result = assistant.assistant_response("Recommend a book", books)

    assert result["intent"] == "recommendation"
    assert len(result["books"]) == 1


def test_recommendation_without_matching_book(monkeypatch):
    monkeypatch.setattr(
        assistant,
        "semantic_detect_intent",
        lambda query: "recommendation"
    )

    monkeypatch.setattr(
        assistant,
        "semantic_search",
        lambda query, books, top_k=5: []
    )

    result = assistant.assistant_response("Recommend a book", books)

    assert result["intent"] == "recommendation"
    assert result["books"] == []# =========================
# UNKNOWN INTENT TEST
# =========================

def test_detect_intent_unknown():
    result = detect_intent("qzxv 92817")

    assert result == "unknown"


# =========================
# SEMANTIC INTENT TESTS
# =========================

def test_semantic_detect_intent_empty_query():
    with patch("ai.smart_assistant.model.encode") as mock_encode:
        result = semantic_detect_intent("")

    assert result == "unknown"
    mock_encode.assert_not_called()


def test_semantic_detect_intent_below_threshold():

    class FakeScores:
        def argmax(self):
            return 0

        def __getitem__(self, index):
            return 0.1

    class FakeSimilarity:
        def __getitem__(self, index):
            return FakeScores()

    with patch(
        "ai.smart_assistant.model.encode",
        return_value=object()
    ), patch(
        "ai.smart_assistant.util.cos_sim",
        return_value=FakeSimilarity()
    ):
        result = semantic_detect_intent("random question")

    assert result == "unknown"


def test_semantic_detect_intent_success():

    class FakeScores:
        def argmax(self):
            return 0

        def __getitem__(self, index):
            return 0.9

    class FakeSimilarity:
        def __getitem__(self, index):
            return FakeScores()

    with patch(
        "ai.smart_assistant.model.encode",
        return_value=object()
    ), patch(
        "ai.smart_assistant.util.cos_sim",
        return_value=FakeSimilarity()
    ):
        result = semantic_detect_intent("Show me available books")

    assert result == "available_books"


# =========================
# ASSISTANT NO MATCHING BOOKS
# =========================

def test_assistant_book_search_no_results():

    with patch(
        "ai.smart_assistant.semantic_detect_intent",
        return_value="book_search"
    ), patch(
        "ai.smart_assistant.semantic_search",
        return_value=[]
    ):
        result = assistant_response(
            "Find books about astronomy",
            []
        )

    assert result["intent"] == "book_search"
    assert result["message"] == "Sorry, I couldn't find matching books."
    assert result["books"] == []