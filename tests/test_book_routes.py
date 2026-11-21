
from unittest.mock import Mock, patch
from app import create_app


def setup_client(student_id=None):
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    if student_id is not None:
        with client.session_transaction() as session:
            session["student_id"] = student_id

    return client


# =========================
# HOME
# =========================

def test_home_success():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = [
        {"Book_ID": 1, "Title": "Python"}
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/")

    assert response.status_code == 200
    fake_cursor.execute.assert_called_once_with(
        "SELECT * FROM Books"
    )
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_home_search():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = [
        {"Book_ID": 1, "Title": "Python"}
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        with patch(
            "app.routes.semantic_search",
            return_value=[{"Book_ID": 1, "Title": "Python"}]
        ) as mock_search:

            response = client.get("/?search=python")

    assert response.status_code == 200
    mock_search.assert_called_once()


def test_home_database_unavailable():
    client = setup_client()

    with patch("app.routes.get_connection", return_value=None):
        response = client.get("/")

    assert response.status_code == 200


# =========================
# RECOMMENDATIONS
# =========================

def test_recommendations_success():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor

    fake_cursor.fetchone.return_value = {
        "Book_ID": 1,
        "Title": "Python"
    }

    fake_cursor.fetchall.return_value = [
        {"Book_ID": 1, "Title": "Python"},
        {"Book_ID": 2, "Title": "Java"}
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        with patch(
            "app.routes.get_recommendations",
            return_value=[{"Book_ID": 2, "Title": "Java"}]
        ) as mock_recommendations:

            response = client.get("/recommend/1")

    assert response.status_code == 200
    mock_recommendations.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_recommendations_book_not_found():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None

    with patch("app.routes.get_connection", return_value=fake_db):
        with patch("app.routes.get_recommendations") as mock_recommendations:
            response = client.get("/recommend/999")

    assert response.status_code == 200
    mock_recommendations.assert_not_called()


def test_recommendations_database_unavailable():
    client = setup_client()

    with patch("app.routes.get_connection", return_value=None):
        response = client.get("/recommend/1")

    assert response.status_code == 200


# =========================
# BOOK DETAILS
# =========================

def test_book_details_success():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = {
        "Book_ID": 1,
        "Title": "Python"
    }

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/book/1")

    assert response.status_code == 200
    fake_cursor.execute.assert_called_once_with(
        "SELECT * FROM Books WHERE Book_ID = %s",
        (1,)
    )


def test_book_details_not_found():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/book/999")

    assert response.status_code == 200


def test_book_details_database_unavailable():
    client = setup_client()

    with patch("app.routes.get_connection", return_value=None):
        response = client.get("/book/1")

    assert response.status_code == 200


# =========================
# ADD FAVORITE
# =========================

def test_add_favorite_requires_login():
    client = setup_client()

    response = client.post("/favorite/1")

    assert response.status_code == 302
    assert response.location == "/login"


def test_add_favorite_success():
    client = setup_client(student_id=5)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/favorite/10")

    assert response.status_code == 302
    assert response.location == "/"

    query, params = fake_cursor.execute.call_args[0]

    assert "INSERT IGNORE INTO Favorites" in query
    assert params == (5, 10)

    fake_db.commit.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_add_favorite_database_unavailable():
    client = setup_client(student_id=5)

    with patch("app.routes.get_connection", return_value=None):
        response = client.post("/favorite/10")

    assert response.status_code == 302
    assert response.location == "/"
