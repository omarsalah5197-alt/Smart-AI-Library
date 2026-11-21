
from unittest.mock import Mock, patch
from app import create_app


def setup_client():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()
    return client


def login_student(client, student_id=1):
    with client.session_transaction() as session:
        session["student_id"] = student_id
        session["student_name"] = "Test Student"
        session["is_admin"] = False


# =========================
# BORROW BOOK TESTS
# =========================

def test_borrow_requires_login():
    client = setup_client()

    response = client.post("/borrow/1", data={"days": "7"})

    assert response.status_code == 302
    assert response.location == "/login"


def test_borrow_success():
    client = setup_client()
    login_student(client)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None
    fake_cursor.rowcount = 1

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/borrow/1", data={"days": "7"})

    assert response.status_code == 302
    assert response.location == "/"
    assert fake_cursor.execute.call_count == 3
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_borrow_prevent_duplicate():
    client = setup_client()
    login_student(client)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = (10,)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/borrow/1", data={"days": "7"})

    assert response.status_code == 302
    assert response.location == "/book/1"
    assert fake_cursor.execute.call_count == 1
    fake_db.commit.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_borrow_unavailable_book():
    client = setup_client()
    login_student(client)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None
    fake_cursor.rowcount = 0

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/borrow/1", data={"days": "7"})

    assert response.status_code == 302
    assert response.location == "/book/1"
    fake_db.rollback.assert_called_once()
    fake_db.commit.assert_not_called()


def test_borrow_invalid_duration():
    client = setup_client()
    login_student(client)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post("/borrow/1", data={"days": "10"})

    assert response.status_code == 302
    assert response.location == "/book/1"
    mock_db.assert_not_called()


def test_borrow_invalid_duration_text():
    client = setup_client()
    login_student(client)

    with patch("app.routes.get_connection") as mock_db:
        response = client.post("/borrow/1", data={"days": "abc"})

    assert response.status_code == 302
    assert response.location == "/book/1"
    mock_db.assert_not_called()


# =========================
# RETURN BOOK TESTS
# =========================

def test_return_requires_login():
    client = setup_client()

    response = client.post("/return-book/10")

    assert response.status_code == 302
    assert response.location == "/login"


def test_return_book_success():
    client = setup_client()
    login_student(client)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = (5,)

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/return-book/10")

    assert response.status_code == 302
    assert response.location == "/my-borrowings"
    assert fake_cursor.execute.call_count == 3
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_return_book_not_owned_or_not_borrowed():
    client = setup_client()
    login_student(client, student_id=2)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post("/return-book/10")

    assert response.status_code == 302
    assert response.location == "/my-borrowings"
    assert fake_cursor.execute.call_count == 1
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_not_called()

# =========================
# LOGOUT TESTS
# =========================

def test_logout_clears_session():
    client = setup_client()
    login_student(client)

    with client.session_transaction() as session:
        session["temporary_data"] = "test"

    response = client.post("/logout")

    assert response.status_code == 302
    assert response.location == "/"

    with client.session_transaction() as session:
        assert len(session) == 0


# =========================
# MY BORROWINGS TESTS
# =========================

def test_my_borrowings_requires_login():
    client = setup_client()

    with patch("app.routes.get_connection") as mock_db:
        response = client.get("/my-borrowings")

    assert response.status_code == 302
    assert response.location == "/login"
    mock_db.assert_not_called()


def test_my_borrowings_success():
    client = setup_client()
    login_student(client, student_id=5)

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchall.return_value = [
        {
            "Borrowing_ID": 10,
            "Book_ID": 2,
            "Title": "Python Programming",
            "Author": "Test Author",
            "Status": "Borrowed"
        }
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.get("/my-borrowings")

    assert response.status_code == 200

    fake_db.cursor.assert_called_once_with(dictionary=True)
    fake_cursor.execute.assert_called_once()

    query, params = fake_cursor.execute.call_args.args

    assert "INNER JOIN Books" in query
    assert "Borrowings.Student_ID = %s" in query
    assert params == (5,)

    fake_cursor.fetchall.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_my_borrowings_database_unavailable():
    client = setup_client()
    login_student(client)

    with patch("app.routes.get_connection", return_value=None):
        response = client.get("/my-borrowings")

    assert response.status_code == 200
