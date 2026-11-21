
from unittest.mock import Mock, patch
from app import create_app


def setup_client(student_id=1):
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["student_id"] = student_id
        session["student_name"] = "Test Student"
        session["is_admin"] = False

    return client


def create_fake_db():
    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = []

    return fake_db, fake_cursor


# =========================
# ACCESS TEST
# =========================

def test_assistant_requires_login():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/assistant")

    assert response.status_code == 302
    assert response.location == "/login"


# =========================
# GET ASSISTANT PAGE
# =========================

def test_assistant_page():
    client = setup_client()

    fake_db, fake_cursor = create_fake_db()

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/assistant")

    assert response.status_code == 200

    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# EMPTY QUESTION
# =========================

def test_assistant_empty_question():
    client = setup_client()

    fake_db, fake_cursor = create_fake_db()

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/assistant",
            data={"query": "   "}
        )

    assert response.status_code == 200

    # Books query should not happen.
    # Only the history query should execute.
    fake_cursor.execute.assert_called_once()

    fake_db.commit.assert_not_called()


# =========================
# ASSISTANT RESPONSE
# =========================

def test_assistant_returns_answer():
    client = setup_client()

    fake_db, fake_cursor = create_fake_db()

    assistant_result = {
        "message": "Here are some available books.",
        "books": []
    }

    with patch(
        "app.routes.get_connection",
        return_value=fake_db
    ), patch(
        "app.routes.detect_intent",
        return_value="available_books"
    ), patch(
        "app.routes.assistant_response",
        return_value=assistant_result
    ):
        response = client.post(
            "/assistant",
            data={"query": "Show available books"}
        )

    assert response.status_code == 200

    # Books query + save chat + history query
    assert fake_cursor.execute.call_count == 3

    fake_db.commit.assert_called_once()


# =========================
# SAVE BOOK TITLES
# =========================

def test_assistant_saves_book_titles():
    client = setup_client()

    fake_db, fake_cursor = create_fake_db()

    assistant_result = {
        "message": "Recommended books:",
        "books": [
            {"Title": "Python Basics"},
            {"Title": "Machine Learning"}
        ]
    }

    with patch(
        "app.routes.get_connection",
        return_value=fake_db
    ), patch(
        "app.routes.detect_intent",
        return_value="book_search"
    ), patch(
        "app.routes.assistant_response",
        return_value=assistant_result
    ):
        response = client.post(
            "/assistant",
            data={"query": "Find Python books"}
        )

    assert response.status_code == 200

    insert_call = fake_cursor.execute.call_args_list[1]

    saved_message = insert_call[0][1][2]

    assert "Python Basics" in saved_message
    assert "Machine Learning" in saved_message


# =========================
# STUDENT HISTORY
# =========================

def test_assistant_history_uses_current_student():
    client = setup_client(student_id=5)

    fake_db, fake_cursor = create_fake_db()

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/assistant")

    assert response.status_code == 200

    query, params = fake_cursor.execute.call_args[0]

    assert "WHERE Student_ID = %s" in query
    assert params == (5,)


# =========================
# BORROWING STATUS
# =========================

def test_assistant_borrowing_status():
    client = setup_client(student_id=5)

    fake_db, fake_cursor = create_fake_db()

    assistant_result = {
        "message": "Your borrowing status.",
        "books": []
    }

    with patch(
        "app.routes.get_connection",
        return_value=fake_db
    ), patch(
        "app.routes.detect_intent",
        return_value="borrowing_status"
    ), patch(
        "app.routes.assistant_response",
        return_value=assistant_result
    ):
        response = client.post(
            "/assistant",
            data={"query": "What are my borrowed books?"}
        )

    assert response.status_code == 200

    assert fake_cursor.execute.call_count == 4

    borrowing_query = fake_cursor.execute.call_args_list[1]

    assert "WHERE Borrowings.Student_ID = %s" in borrowing_query[0][0]
    assert borrowing_query[0][1] == (5,)
