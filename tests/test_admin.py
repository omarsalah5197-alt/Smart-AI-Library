
from unittest.mock import Mock, patch
from app import create_app


def setup_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def login_user(client, is_admin=False):
    with client.session_transaction() as session:
        session["student_id"] = 1
        session["student_name"] = "Test Student"
        session["is_admin"] = is_admin


# =========================
# ACCESS CONTROL TESTS
# =========================

def test_admin_dashboard_requires_login():
    client = setup_client()

    response = client.get("/admin")

    assert response.status_code == 302
    assert response.location == "/login"


def test_admin_dashboard_blocks_student():
    client = setup_client()
    login_user(client, is_admin=False)

    response = client.get("/admin")

    assert response.status_code == 302
    assert response.location == "/"


def test_admin_dashboard_allows_admin():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = []

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/admin")

    assert response.status_code == 200
    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_admin_borrowings_requires_login():
    client = setup_client()

    response = client.get("/admin/borrowings")

    assert response.status_code == 302
    assert response.location == "/login"


def test_admin_borrowings_blocks_student():
    client = setup_client()
    login_user(client, is_admin=False)

    response = client.get("/admin/borrowings")

    assert response.status_code == 302
    assert response.location == "/"


def test_admin_borrowings_allows_admin():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = []

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/admin/borrowings")

    assert response.status_code == 200
    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# ADD BOOK TESTS
# =========================

def test_add_book_blocks_student():
    client = setup_client()
    login_user(client, is_admin=False)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(
            "/admin/add-book",
            data={"title": "Test Book", "copies": "5"}
        )

    assert response.status_code == 302
    assert response.location == "/"
    mock_db.assert_not_called()


def test_add_book_success():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/admin/add-book",
            data={
                "title": "Python Basics",
                "author": "Test Author",
                "category": "Programming",
                "description": "A test book",
                "copies": "5"
            }
        )

    assert response.status_code == 302
    assert response.location == "/admin"
    fake_cursor.execute.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_add_book_rejects_empty_title():
    client = setup_client()
    login_user(client, is_admin=True)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(
            "/admin/add-book",
            data={"title": "   ", "copies": "5"}
        )

    assert response.status_code == 302
    assert response.location == "/admin"
    mock_db.assert_not_called()


# =========================
# EDIT BOOK TESTS
# =========================

def test_edit_book_blocks_student():
    client = setup_client()
    login_user(client, is_admin=False)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(
            "/admin/edit-book/1",
            data={"title": "Updated Book", "copies": "3"}
        )

    assert response.status_code == 302
    assert response.location == "/"
    mock_db.assert_not_called()


def test_edit_book_success():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/admin/edit-book/1",
            data={
                "title": "Updated Book",
                "author": "Updated Author",
                "category": "Technology",
                "description": "Updated description",
                "copies": "4"
            }
        )

    assert response.status_code == 302
    assert response.location == "/admin"
    fake_cursor.execute.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


# =========================
# DELETE BOOK TESTS
# =========================

def test_delete_book_blocks_student():
    client = setup_client()
    login_user(client, is_admin=False)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post("/admin/delete-book/1")

    assert response.status_code == 302
    assert response.location == "/"
    mock_db.assert_not_called()


def test_delete_book_with_borrowings():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = (2,)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/admin/delete-book/1")

    assert response.status_code == 302
    assert response.location == "/admin"
    assert fake_cursor.execute.call_count == 1
    fake_db.commit.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_delete_book_success():
    client = setup_client()
    login_user(client, is_admin=True)

    fake_db = Mock()
    fake_cursor = Mock()
    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = (0,)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/admin/delete-book/1")

    assert response.status_code == 302
    assert response.location == "/admin"
    assert fake_cursor.execute.call_count == 3
    fake_db.commit.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()
