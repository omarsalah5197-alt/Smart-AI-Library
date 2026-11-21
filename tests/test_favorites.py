

from unittest.mock import Mock, patch
from flask import url_for
from app import create_app


def setup_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def login_student(client, student_id=1):
    with client.session_transaction() as session:
        session["student_id"] = student_id
        session["student_name"] = "Test Student"
        session["is_admin"] = False


def get_route(client, endpoint, **values):
    with client.application.test_request_context():
        return url_for(endpoint, **values)


# =========================
# FAVORITES TESTS
# =========================

def test_favorites_requires_login():
    client = setup_client()
    url = get_route(client, "favorites")

    response = client.get(url)

    assert response.status_code == 302
    assert response.location == "/login"


def test_favorites_success():
    client = setup_client()
    login_student(client)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = [
        {"Book_ID": 1, "Title": "Python"}
    ]

    url = get_route(client, "favorites")

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get(url)

    assert response.status_code == 200
    fake_cursor.execute.assert_called_once()

    query, params = fake_cursor.execute.call_args.args
    assert "INNER JOIN Favorites" in query
    assert params == (1,)

    fake_cursor.fetchall.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_favorites_database_unavailable():
    client = setup_client()
    login_student(client)

    url = get_route(client, "favorites")

    with patch("app.routes.get_connection", return_value=None):
        response = client.get(url)

    assert response.status_code == 200


# =========================
# REMOVE FAVORITE TESTS
# =========================

def test_remove_favorite_requires_login():
    client = setup_client()
    url = get_route(client, "remove_favorite", book_id=1)

    response = client.post(url)

    assert response.status_code == 302
    assert response.location == "/login"


def test_remove_favorite_success():
    client = setup_client()
    login_student(client, student_id=5)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor

    url = get_route(client, "remove_favorite", book_id=10)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(url)

    assert response.status_code == 302
    assert response.location == "/favorites"

    fake_cursor.execute.assert_called_once()

    query, params = fake_cursor.execute.call_args.args
    assert "DELETE FROM Favorites" in query
    assert params == (10, 5)

    fake_db.commit.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_remove_favorite_database_unavailable():
    client = setup_client()
    login_student(client)

    url = get_route(client, "remove_favorite", book_id=1)

    with patch("app.routes.get_connection", return_value=None):
        response = client.post(url)

    assert response.status_code == 302
    assert response.location == "/favorites"
