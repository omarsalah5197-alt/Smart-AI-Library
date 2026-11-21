
from unittest.mock import Mock, patch
import mysql.connector
import runpy

from database.connection import get_connection
from config import DB_CONFIG


def test_database_connection_success():
    fake_connection = Mock()
    fake_connection.is_connected.return_value = True

    with patch(
        "database.connection.mysql.connector.connect",
        return_value=fake_connection
    ) as mock_connect:

        result = get_connection()

        assert result is fake_connection
        mock_connect.assert_called_once_with(**DB_CONFIG)


def test_database_connection_failure():
    with patch(
        "database.connection.mysql.connector.connect",
        side_effect=mysql.connector.Error("Connection failed")
    ):
        result = get_connection()

        assert result is None


def test_database_connection_not_connected():
    fake_connection = Mock()
    fake_connection.is_connected.return_value = False

    with patch(
        "database.connection.mysql.connector.connect",
        return_value=fake_connection
    ):
        result = get_connection()

        assert result is None


def test_database_main_connection_success():
    fake_connection = Mock()
    fake_connection.is_connected.return_value = True

    with patch(
        "mysql.connector.connect",
        return_value=fake_connection
    ) as mock_connect, patch("builtins.print") as mock_print:

        runpy.run_path(
            "database/connection.py",
            run_name="__main__"
        )

    mock_connect.assert_called_once_with(**DB_CONFIG)

    mock_print.assert_called_once_with(
        "MySQL Connected Successfully!"
    )

    fake_connection.close.assert_called_once()
