from flask import render_template, request, redirect, session, flash
from ai.smart_assistant import assistant_response, detect_intent
from ai.smart_assistant import detect_intent, assistant_response
from datetime import date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import get_connection
from ai.smart_search import semantic_search
from ai.recommendation import get_recommendations


def home():
    books = []
    search = request.args.get("search", "").strip()

    db = get_connection()

    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Books")
        all_books = cursor.fetchall()

        if search:
            books = semantic_search(search, all_books)
        else:
            books = all_books

        cursor.close()
        db.close()

    return render_template("index.html", books=books, search=search)


def recommendations(book_id):
    db = get_connection()
    books = []
    selected_book = None

    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Books WHERE Book_ID = %s", (book_id,))
        selected_book = cursor.fetchone()

        if selected_book:
            cursor.execute("SELECT * FROM Books")
            all_books = cursor.fetchall()
            books = get_recommendations(selected_book, all_books, limit=3)

        cursor.close()
        db.close()

    return render_template("recommendations.html", books=books)


def book_details(book_id):
    db = get_connection()
    book = None

    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Books WHERE Book_ID = %s", (book_id,))
        book = cursor.fetchone()

        cursor.close()
        db.close()

    return render_template("book_details.html", book=book)


def add_favorite(book_id):
    if "student_id" not in session:
        return redirect("/login")

    db = get_connection()

    if db:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT IGNORE INTO Favorites (Student_ID, Book_ID)
            VALUES (%s, %s)
            """,
            (session["student_id"], book_id),
        )
        db.commit()
        cursor.close()
        db.close()

    return redirect("/")


def favorites():
    if "student_id" not in session:
        return redirect("/login")

    db = get_connection()
    books = []

    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT Books.*
            FROM Books
            INNER JOIN Favorites
            ON Books.Book_ID = Favorites.Book_ID
            WHERE Favorites.Student_ID = %s
            """,
            (session["student_id"],),
        )

        books = cursor.fetchall()
        cursor.close()
        db.close()

    return render_template("favorites.html", books=books)


def remove_favorite(book_id):
    if "student_id" not in session:
        return redirect("/login")

    db = get_connection()

    if db:
        cursor = db.cursor()
        cursor.execute(
            """
            DELETE FROM Favorites
            WHERE Book_ID = %s AND Student_ID = %s
            """,
            (book_id, session["student_id"]),
        )
        db.commit()
        cursor.close()
        db.close()

    return redirect("/favorites")


def register():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            message = "Please fill in all fields."
        else:
            db = get_connection()

            if db:
                cursor = db.cursor(dictionary=True)

                cursor.execute(
                    "SELECT Student_ID FROM Students WHERE Email = %s", (email,)
                )
                existing_student = cursor.fetchone()

                if existing_student:
                    message = "Email already exists."
                else:
                    hashed_password = generate_password_hash(password)

                    cursor.execute(
                        """
                        INSERT INTO Students (Name, Email, Password)
                        VALUES (%s, %s, %s)
                        """,
                        (name, email, hashed_password),
                    )

                    db.commit()
                    cursor.close()
                    db.close()

                    return redirect("/login")

                cursor.close()
                db.close()

    return render_template("register.html", message=message)


def login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        db = get_connection()

        if db:
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute("SELECT * FROM Students WHERE Email = %s", (email,))

                student = cursor.fetchone()

                if student and check_password_hash(student["Password"], password):
                    session["student_id"] = student["Student_ID"]
                    session["student_name"] = student["Name"]
                    session["is_admin"] = bool(student["Is_Admin"])

                    return redirect("/")

                message = "Invalid email or password."

            finally:
                cursor.close()
                db.close()

    return render_template("login.html", message=message)


def logout():
    session.clear()
    return redirect("/")


def my_borrowings():
    if "student_id" not in session:
        return redirect("/login")

    db = get_connection()
    borrowings = []

    if db:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                Borrowings.*,
                Books.Title,
                Books.Author
            FROM Borrowings
            INNER JOIN Books
                ON Borrowings.Book_ID = Books.Book_ID
            WHERE Borrowings.Student_ID = %s
            ORDER BY Borrowings.Borrowing_ID DESC
            """,
            (session["student_id"],),
        )

        borrowings = cursor.fetchall()

        cursor.close()
        db.close()

    return render_template("my_borrowings.html", borrowings=borrowings)


def borrow_book(book_id):
    if "student_id" not in session:
        return redirect("/login")

    if request.method != "POST":
        return redirect(f"/book/{book_id}")

    try:
        days = int(request.form.get("days", 7))
    except ValueError:
        return redirect(f"/book/{book_id}")

    if days not in [7, 14, 21]:
        return redirect(f"/book/{book_id}")

    db = get_connection()

    if db:
        cursor = db.cursor()

        try:
            # Check if this student already borrowed this book
            cursor.execute(
                """
                SELECT Borrowing_ID
                FROM Borrowings
                WHERE Student_ID = %s
                AND Book_ID = %s
                AND Status = 'Borrowed'
                """,
                (session["student_id"], book_id),
            )

            existing_borrowing = cursor.fetchone()

            if existing_borrowing:
                flash(
                    "You have already borrowed this book. Please return it first.",
                    "warning",
                )
                return redirect(f"/book/{book_id}")
            # Reduce available copies
            cursor.execute(
                """
                UPDATE Books
                SET Available_Copies = Available_Copies - 1
                WHERE Book_ID = %s
                AND Available_Copies > 0
                """,
                (book_id,),
            )

            if cursor.rowcount == 0:
                db.rollback()
                return redirect(f"/book/{book_id}")

            borrow_date = date.today()
            due_date = borrow_date + timedelta(days=days)

            cursor.execute(
                """
                INSERT INTO Borrowings
                (Student_ID, Book_ID, Borrow_Date, Due_Date, Status)
                VALUES (%s, %s, %s, %s, 'Borrowed')
                """,
                (session["student_id"], book_id, borrow_date, due_date),
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    return redirect("/")


def return_book(borrowing_id):
    if "student_id" not in session:
        return redirect("/login")

    db = get_connection()

    if db:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT Book_ID
                FROM Borrowings
                WHERE Borrowing_ID = %s
                AND Student_ID = %s
                AND Status = 'Borrowed'
                """,
                (borrowing_id, session["student_id"]),
            )

            borrowing = cursor.fetchone()

            if borrowing:
                book_id = borrowing[0]

                cursor.execute(
                    """
                    UPDATE Borrowings
                    SET Status = 'Returned',
                        Return_Date = %s
                    WHERE Borrowing_ID = %s
                    """,
                    (date.today(), borrowing_id),
                )

                cursor.execute(
                    """
                    UPDATE Books
                    SET Available_Copies = Available_Copies + 1
                    WHERE Book_ID = %s
                    """,
                    (book_id,),
                )

                db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    return redirect("/my-borrowings")


def admin_dashboard():
    if "student_id" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/")

    db = get_connection()
    books = []

    if db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Books ORDER BY Book_ID DESC")
        books = cursor.fetchall()
        cursor.close()
        db.close()

    return render_template("admin_dashboard.html", books=books)


def add_book():
    if "student_id" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        try:
            copies = int(request.form.get("copies", 0))
        except ValueError:
            return redirect("/admin")

        if not title or copies < 0:
            return redirect("/admin")

        db = get_connection()

        if db:
            cursor = db.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO Books
                    (Title, Author, Category, Description, Available_Copies)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (title, author, category, description, copies),
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                cursor.close()
                db.close()

    return redirect("/admin")


def edit_book(book_id):
    if "student_id" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/")

    db = get_connection()

    if not db:
        return redirect("/admin")

    cursor = db.cursor(dictionary=True)

    try:
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()

            try:
                copies = int(request.form.get("copies", 0))
            except ValueError:
                return redirect("/admin")

            if not title or copies < 0:
                return redirect("/admin")

            cursor.execute(
                """
                UPDATE Books
                SET Title = %s,
                    Author = %s,
                    Category = %s,
                    Description = %s,
                    Available_Copies = %s
                WHERE Book_ID = %s
                """,
                (title, author, category, description, copies, book_id),
            )

            db.commit()
            return redirect("/admin")

        cursor.execute("SELECT * FROM Books WHERE Book_ID = %s", (book_id,))
        book = cursor.fetchone()

        if not book:
            return redirect("/admin")

        return render_template("edit_book.html", book=book)

    finally:
        cursor.close()
        db.close()


def delete_book(book_id):
    if "student_id" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/")

    db = get_connection()

    if db:
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Borrowings
                WHERE Book_ID = %s
                """,
                (book_id,),
            )

            borrowing_count = cursor.fetchone()[0]

            if borrowing_count > 0:
                return redirect("/admin")

            cursor.execute("DELETE FROM Favorites WHERE Book_ID = %s", (book_id,))

            cursor.execute("DELETE FROM Books WHERE Book_ID = %s", (book_id,))

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            cursor.close()
            db.close()

    return redirect("/admin")


def admin_borrowings():
    if "student_id" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/")

    db = get_connection()
    borrowings = []

    if db:
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    Borrowings.Borrowing_ID,
                    Students.Name AS Student_Name,
                    Books.Title AS Book_Title,
                    Borrowings.Borrow_Date,
                    Borrowings.Due_Date,
                    Borrowings.Return_Date,
                    Borrowings.Status
                FROM Borrowings
                INNER JOIN Students
                    ON Borrowings.Student_ID = Students.Student_ID
                INNER JOIN Books
                    ON Borrowings.Book_ID = Books.Book_ID
                ORDER BY Borrowings.Borrowing_ID DESC
                """)

            borrowings = cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    return render_template("admin_borrowings.html", borrowings=borrowings)

def smart_assistant():
    if "student_id" not in session:
        return redirect("/login")

    answer = None
    query = ""
    history = []

    db = get_connection()

    if db:
        cursor = db.cursor(dictionary=True)

        try:
            if request.method == "POST":
                query = request.form.get("query", "").strip()

                if query:
                    cursor.execute("SELECT * FROM Books")
                    books = cursor.fetchall()

                    borrowings = []
                    intent = detect_intent(query)

                    if intent == "borrowing_status":
                        cursor.execute("""
                            SELECT
                                Borrowings.Borrowing_ID,
                                Books.Title AS Book_Title,
                                Borrowings.Borrow_Date,
                                Borrowings.Due_Date,
                                Borrowings.Return_Date,
                                Borrowings.Status
                            FROM Borrowings
                            INNER JOIN Books
                                ON Borrowings.Book_ID = Books.Book_ID
                            WHERE Borrowings.Student_ID = %s
                            ORDER BY Borrowings.Borrowing_ID DESC
                        """, (session["student_id"],))

                        borrowings = cursor.fetchall()

                    answer = assistant_response(
                        query,
                        books,
                        borrowings
                    )

                    # Prepare the assistant response for saving
                    response_text = answer["message"]

                    if answer.get("books"):
                        titles = [
                            str(book.get("Title") or book.get("Book_Title") or "")
                            for book in answer["books"]
                        ]
                        titles = [title for title in titles if title]

                        if titles:
                            response_text += "\nBooks: " + ", ".join(titles)

                    # Save the conversation
                    cursor.execute("""
                        INSERT INTO Chat_History
                        (Student_ID, User_Message, Assistant_Response)
                        VALUES (%s, %s, %s)
                    """, (
                        session["student_id"],
                        query,
                        response_text
                    ))

                    current_chat_id = cursor.lastrowid
                    db.commit()

                else:
                    current_chat_id = None
            else:
                current_chat_id = None

            # Get the student's previous conversations
            if current_chat_id:
                cursor.execute("""
                    SELECT *
                    FROM Chat_History
                    WHERE Student_ID = %s
                    AND Chat_ID != %s
                    ORDER BY Created_At DESC, Chat_ID DESC
                    LIMIT 20
                """, (session["student_id"], current_chat_id))
            else:
                cursor.execute("""
                    SELECT *
                    FROM Chat_History
                    WHERE Student_ID = %s
                    ORDER BY Created_At DESC, Chat_ID DESC
                    LIMIT 20
                """, (session["student_id"],))

            history = cursor.fetchall()

        finally:
            cursor.close()
            db.close()

    return render_template(
        "smart_assistant.html",
        answer=answer,
        query=query,
        history=history
    )