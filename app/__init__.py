import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("SECRET_KEY")
    app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV") == "production"
)

    from app.routes import (
        home,
        recommendations,
        book_details,
        add_favorite,
        favorites,
        remove_favorite,
        register,
        login,
        logout,
        my_borrowings,
        borrow_book,
        return_book,
        admin_dashboard,
        admin_borrowings,
        add_book,
        edit_book,
        delete_book,
        smart_assistant
    )

    app.add_url_rule("/", "home", home)

    app.add_url_rule(
        "/recommend/<int:book_id>",
        "recommendations",
        recommendations
    )

    app.add_url_rule(
        "/book/<int:book_id>",
        "book_details",
        book_details
    )

    app.add_url_rule(
        "/favorite/<int:book_id>",
        "add_favorite",
        add_favorite,
        methods=["POST"]
    )

    app.add_url_rule(
        "/favorites",
        "favorites",
        favorites
    )

    app.add_url_rule(
        "/remove-favorite/<int:book_id>",
        "remove_favorite",
        remove_favorite,
        methods=["POST"]
    )

    app.add_url_rule(
        "/register",
        "register",
        register,
        methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/login",
        "login",
        login,
        methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/logout",
        "logout",
        logout,
        methods=["POST"]
    )

    app.add_url_rule(
        "/my-borrowings",
        "my_borrowings",
        my_borrowings
    )

    app.add_url_rule(
        "/borrow/<int:book_id>",
        "borrow_book",
        borrow_book,
        methods=["POST"]
    )

    app.add_url_rule(
        "/return-book/<int:borrowing_id>",
        "return_book",
        return_book,
        methods=["POST"]
    )

    app.add_url_rule(
        "/admin",
        "admin_dashboard",
        admin_dashboard
    )

    app.add_url_rule(
        "/admin/add-book",
        "add_book",
        add_book,
        methods=["POST"]
    )

    app.add_url_rule(
        "/admin/edit-book/<int:book_id>",
        "edit_book",
        edit_book,
        methods=["GET", "POST"]
    )

    app.add_url_rule(
        "/admin/delete-book/<int:book_id>",
        "delete_book",
        delete_book,
        methods=["POST"]
    )

    app.add_url_rule(
        "/admin/borrowings",
        "admin_borrowings",
        admin_borrowings
    )
    app.add_url_rule(
    "/assistant",
    "smart_assistant",
    smart_assistant,
    methods=["GET", "POST"]
)

    return app