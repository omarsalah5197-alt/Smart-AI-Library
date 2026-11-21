
from app import create_app


def test_app_creation():
    app = create_app()

    assert app is not None
    assert app.secret_key is not None


def test_routes_registration():
    app = create_app()

    routes = {
        "/": "home",
        "/recommend/<int:book_id>": "recommendations",
        "/book/<int:book_id>": "book_details",
        "/favorite/<int:book_id>": "add_favorite",
        "/favorites": "favorites",
        "/remove-favorite/<int:book_id>": "remove_favorite",
        "/register": "register",
        "/login": "login",
        "/logout": "logout",
        "/my-borrowings": "my_borrowings",
        "/borrow/<int:book_id>": "borrow_book",
        "/return-book/<int:borrowing_id>": "return_book",
        "/admin": "admin_dashboard",
        "/admin/add-book": "add_book",
        "/admin/edit-book/<int:book_id>": "edit_book",
        "/admin/delete-book/<int:book_id>": "delete_book",
        "/admin/borrowings": "admin_borrowings",
        "/assistant": "smart_assistant",
    }

    registered_routes = {
        rule.rule: rule.endpoint
        for rule in app.url_map.iter_rules()
    }

    for path, endpoint in routes.items():
        assert registered_routes.get(path) == endpoint


def test_post_routes_methods():
    app = create_app()

    post_routes = {
        "add_favorite",
        "remove_favorite",
        "logout",
        "borrow_book",
        "return_book",
        "add_book",
        "delete_book",
    }

    for rule in app.url_map.iter_rules():
        if rule.endpoint in post_routes:
            assert "POST" in rule.methods
