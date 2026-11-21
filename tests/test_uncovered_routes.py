from flask import session
from app.routes import borrow_book
import pytest
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


def login_admin(client):
    with client.session_transaction() as session:
        session["student_id"] = 1
        session["student_name"] = "Test Admin"
        session["is_admin"] = True


def route_url(client, endpoint, **values):
    with client.application.test_request_context():
        return url_for(endpoint, **values)


def make_fake_db():
    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor
    return fake_db, fake_cursor


# =========================
# BORROW BOOK EXTRA TESTS
# =========================

def test_borrow_get_request_redirects_to_book():
    client = setup_client()

    with client.application.test_request_context(
        "/borrow/1",
        method="GET"
    ):
        session["student_id"] = 1

        with patch("app.routes.get_connection") as mock_db:
            response = borrow_book(1)

    assert response.status_code == 302
    assert response.location == "/book/1"
    mock_db.assert_not_called()

def test_borrow_database_exception():
    client = setup_client()
    login_student(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.execute.side_effect = RuntimeError("Database error")

    url = route_url(client, "borrow_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        with pytest.raises(RuntimeError):
            client.post(url, data={"days": "7"})

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# RETURN BOOK EXTRA TESTS
# =========================

def test_return_book_database_exception():
    client = setup_client()
    login_student(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.execute.side_effect = RuntimeError("Database error")

    url = route_url(client, "return_book", borrowing_id=10)

    with patch("app.routes.get_connection", return_value=fake_db):
        with pytest.raises(RuntimeError):
            client.post(url)

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# ADMIN LOGIN TESTS
# =========================

@pytest.mark.parametrize(
    "endpoint, method, values",
    [
        ("admin_dashboard", "get", {}),
        ("add_book", "post", {}),
        ("edit_book", "get", {"book_id": 1}),
        ("delete_book", "post", {"book_id": 1}),
        ("admin_borrowings", "get", {}),
    ],
)
def test_admin_routes_require_login(endpoint, method, values):
    client = setup_client()
    url = route_url(client, endpoint, **values)

    response = getattr(client, method)(url)

    assert response.status_code == 302
    assert response.location == "/login"


@pytest.mark.parametrize(
    "endpoint, method, values",
    [
        ("admin_dashboard", "get", {}),
        ("add_book", "post", {}),
        ("edit_book", "get", {"book_id": 1}),
        ("delete_book", "post", {"book_id": 1}),
        ("admin_borrowings", "get", {}),
    ],
)
def test_admin_routes_reject_normal_student(endpoint, method, values):
    client = setup_client()
    login_student(client)

    url = route_url(client, endpoint, **values)

    response = getattr(client, method)(url)

    assert response.status_code == 302
    assert response.location == "/"


# =========================
# ADD BOOK EXTRA TESTS
# =========================

def test_add_book_invalid_copies():
    client = setup_client()
    login_admin(client)

    data = {
        "title": "Python",
        "author": "Test Author",
        "category": "Programming",
        "description": "Test Description",
        "copies": "abc",
    }

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(route_url(client, "add_book"), data=data)

    assert response.status_code == 302
    assert response.location == "/admin"
    mock_db.assert_not_called()


@pytest.mark.parametrize(
    "data",
    [
        {
            "title": "",
            "author": "Test Author",
            "category": "Programming",
            "description": "Test",
            "copies": "3",
        },
        {
            "title": "Python",
            "author": "Test Author",
            "category": "Programming",
            "description": "Test",
            "copies": "-1",
        },
    ],
)
def test_add_book_invalid_data(data):
    client = setup_client()
    login_admin(client)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(route_url(client, "add_book"), data=data)

    assert response.status_code == 302
    assert response.location == "/admin"
    mock_db.assert_not_called()


def test_add_book_database_unavailable():
    client = setup_client()
    login_admin(client)

    data = {
        "title": "Python",
        "author": "Test Author",
        "category": "Programming",
        "description": "Test",
        "copies": "3",
    }

    with patch("app.routes.get_connection", return_value=None):
        response = client.post(route_url(client, "add_book"), data=data)

    assert response.status_code == 302
    assert response.location == "/admin"


def test_add_book_database_exception():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.execute.side_effect = RuntimeError("Database error")

    data = {
        "title": "Python",
        "author": "Test Author",
        "category": "Programming",
        "description": "Test",
        "copies": "3",
    }

    with patch("app.routes.get_connection", return_value=fake_db):
        with pytest.raises(RuntimeError):
            client.post(route_url(client, "add_book"), data=data)

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# EDIT BOOK EXTRA TESTS
# =========================

def test_edit_book_database_unavailable():
    client = setup_client()
    login_admin(client)

    url = route_url(client, "edit_book", book_id=1)

    with patch("app.routes.get_connection", return_value=None):
        response = client.get(url)

    assert response.status_code == 302
    assert response.location == "/admin"


def test_edit_book_not_found():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.fetchone.return_value = None

    url = route_url(client, "edit_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get(url)

    assert response.status_code == 302
    assert response.location == "/admin"

    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_edit_book_get_success():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()

    fake_cursor.fetchone.return_value = {
        "Book_ID": 1,
        "Title": "Python Programming",
        "Author": "Test Author",
        "Category": "Programming",
        "Description": "Test Description",
        "Available_Copies": 5,
    }

    url = route_url(client, "edit_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get(url)

    assert response.status_code == 200
    assert b"Python Programming" in response.data

    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_edit_book_invalid_copies():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()

    data = {
        "title": "Python",
        "author": "Test Author",
        "category": "Programming",
        "description": "Test",
        "copies": "abc",
    }

    url = route_url(client, "edit_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert response.location == "/admin"

    fake_cursor.execute.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


@pytest.mark.parametrize(
    "data",
    [
        {
            "title": "",
            "author": "Test Author",
            "category": "Programming",
            "description": "Test",
            "copies": "3",
        },
        {
            "title": "Python",
            "author": "Test Author",
            "category": "Programming",
            "description": "Test",
            "copies": "-1",
        },
    ],
)
def test_edit_book_invalid_data(data):
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()

    url = route_url(client, "edit_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert response.location == "/admin"

    fake_cursor.execute.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# DELETE BOOK EXTRA TESTS
# =========================

def test_delete_book_has_active_borrowings():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.fetchone.return_value = (2,)

    url = route_url(client, "delete_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(url)

    assert response.status_code == 302
    assert response.location == "/admin"

    fake_cursor.execute.assert_called_once()
    fake_db.commit.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_delete_book_database_exception():
    client = setup_client()
    login_admin(client)

    fake_db, fake_cursor = make_fake_db()
    fake_cursor.execute.side_effect = RuntimeError("Database error")

    url = route_url(client, "delete_book", book_id=1)

    with patch("app.routes.get_connection", return_value=fake_db):
        with pytest.raises(RuntimeError):
            client.post(url)

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()
