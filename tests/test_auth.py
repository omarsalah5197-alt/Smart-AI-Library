
from unittest.mock import Mock, patch
from werkzeug.security import generate_password_hash

from app import create_app


def setup_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


# Test 1: Open register page
def test_register_page():
    client = setup_client()

    response = client.get("/register")

    assert response.status_code == 200


# Test 2: Register with missing fields
def test_register_missing_fields():
    client = setup_client()

    with patch("app.routes.get_connection") as mock_db:
        response = client.post(
            "/register",
            data={
                "name": "",
                "email": "",
                "password": ""
            }
        )

    assert response.status_code == 200
    assert b"Please fill in all fields." in response.data
    mock_db.assert_not_called()


# Test 3: Register with existing email
def test_register_existing_email():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = {"Student_ID": 1}

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/register",
            data={
                "name": "Test Student",
                "email": "test@example.com",
                "password": "test123"
            }
        )

    assert response.status_code == 200
    assert b"Email already exists." in response.data
    fake_db.close.assert_called_once()


# Test 4: Successful registration
def test_register_success():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/register",
            data={
                "name": "New Student",
                "email": "new@example.com",
                "password": "test123"
            }
        )

    assert response.status_code == 302
    assert response.location == "/login"
    fake_db.commit.assert_called_once()


# Test 5: Open login page
def test_login_page():
    client = setup_client()

    response = client.get("/login")

    assert response.status_code == 200


# Test 6: Login with invalid email or password
def test_login_invalid_credentials():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor
    fake_cursor.fetchone.return_value = None

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/login",
            data={
                "email": "wrong@example.com",
                "password": "wrong123"
            }
        )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


# Test 7: Successful student login
def test_login_success():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_cursor.fetchone.return_value = {
        "Student_ID": 10,
        "Name": "Test Student",
        "Password": generate_password_hash("test123"),
        "Is_Admin": 0
    }

    fake_db.cursor.return_value = fake_cursor

    with patch("app.routes.get_connection", return_value=fake_db):
        response = client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "test123"
            }
        )

    assert response.status_code == 302
    assert response.location == "/"

    with client.session_transaction() as session:
        assert session["student_id"] == 10
        assert session["student_name"] == "Test Student"
        assert session["is_admin"] is False
