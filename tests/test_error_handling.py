
from unittest.mock import Mock, patch
from app import create_app


def setup_client():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["student_id"] = 1
        session["student_name"] = "Test Student"
        session["is_admin"] = True

    return client


def test_add_book_database_error():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor

    fake_cursor.execute.side_effect = Exception("Database Error")

    with patch("app.routes.get_connection", return_value=fake_db):
        try:
            client.post(
                "/admin/add-book",
                data={
                    "title": "Test Book",
                    "author": "Author",
                    "category": "Programming",
                    "description": "Test",
                    "copies": "5"
                }
            )
            assert False, "Expected database exception"
        except Exception as error:
            assert str(error) == "Database Error"

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_borrow_book_database_error():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor

    fake_cursor.fetchone.return_value = None

    fake_cursor.execute.side_effect = [
        None,
        None,
        Exception("Insert Error")
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        try:
            client.post(
                "/borrow/1",
                data={"days": "7"}
            )
            assert False, "Expected database exception"
        except Exception as error:
            assert str(error) == "Insert Error"

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()


def test_delete_book_database_error():
    client = setup_client()

    fake_db = Mock()
    fake_cursor = Mock()

    fake_db.cursor.return_value = fake_cursor

    fake_cursor.fetchone.return_value = (0,)

    fake_cursor.execute.side_effect = [
        None,
        None,
        Exception("Delete Error")
    ]

    with patch("app.routes.get_connection", return_value=fake_db):
        try:
            client.post("/admin/delete-book/1")
            assert False, "Expected database exception"
        except Exception as error:
            assert str(error) == "Delete Error"

    fake_db.rollback.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_db.close.assert_called_once()
