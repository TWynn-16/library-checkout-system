"""
Library Management System backend.

Install the connector:
    python -m pip install mysql-connector-python

Set the database connection environment variables before running the application:
    LIBRARY_DB_HOST (default: localhost)
    LIBRARY_DB_USER (default: root)
    LIBRARY_DB_PASSWORD
    LIBRARY_DB_NAME (default: library_management)

This module contains database operations and Open Library API search logic.
The Tkinter frontend should call these functions instead of changing a Python
list named `books`.
"""

import json
import os
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import mysql.connector
from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="DB_PASSWORD",
        database="library_management"
    )



def _get_or_create_id(cursor, table, id_column, name_column, value):
    """Find a lookup-table row by name, creating it if necessary."""
    # Table and column names are internal constants supplied by this module.
    cursor.execute(
        f"SELECT {id_column} FROM {table} WHERE {name_column} = %s",
        (value.strip(),),
    )
    result = cursor.fetchone()
    if result:
        return result[0]

    cursor.execute(
        f"INSERT INTO {table} ({name_column}) VALUES (%s)",
        (value.strip(),),
    )
    return cursor.lastrowid


def get_books(search_text="", sort_by="title"):
    """Return books with author, category, and current loan status."""
    allowed_sorts = {
        "title": "b.title",
        "author": "a.author_name",
        "category": "c.category_name",
        "year": "b.publication_year",
    }
    order_column = allowed_sorts.get(sort_by, "b.title")
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        search = f"%{search_text.strip()}%"
        cursor.execute(
            f"""
            SELECT b.book_id, b.title, a.author_name, c.category_name,
                   b.publication_year, b.isbn,
                   CASE
                     WHEN l.loan_id IS NOT NULL AND l.due_date < CURRENT_DATE
                       THEN 'Overdue'
                     WHEN l.loan_id IS NOT NULL THEN 'Checked Out'
                     ELSE 'Available'
                   END AS status,
                   CONCAT(m.first_name, ' ', m.last_name) AS borrower,
                   l.checkout_date, l.due_date
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            JOIN categories c ON b.category_id = c.category_id
            LEFT JOIN loans l
              ON b.book_id = l.book_id AND l.return_date IS NULL
            LEFT JOIN members m ON l.member_id = m.member_id
            WHERE b.title LIKE %s OR a.author_name LIKE %s
                  OR c.category_name LIKE %s
            ORDER BY {order_column}
            """,
            (search, search, search),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def add_book(title, author, category, publication_year=None, isbn=None):
    """Create a book and its author/category lookup rows if needed."""
    if not title or not title.strip():
        raise ValueError("Book title is required.")
    if not author or not author.strip():
        raise ValueError("Author is required.")
    if not category or not category.strip():
        raise ValueError("Category is required.")

    if publication_year in ("", None):
        publication_year = None
    else:
        publication_year = int(publication_year)
        if not 1 <= publication_year <= 2100:
            raise ValueError("Enter a valid publication year.")

    connection = get_connection()
    try:
        connection.start_transaction()
        cursor = connection.cursor()
        author_id = _get_or_create_id(
            cursor, "authors", "author_id", "author_name", author
        )
        category_id = _get_or_create_id(
            cursor, "categories", "category_id", "category_name", category
        )
        cursor.execute(
            """
            INSERT INTO books (title, author_id, category_id, publication_year, isbn)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title.strip(), author_id, category_id, publication_year,
             isbn.strip() if isbn and isbn.strip() else None),
        )
        book_id = cursor.lastrowid
        connection.commit()
        return book_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def update_book(book_id, title, author, category, publication_year=None, isbn=None):
    """Update a book's details."""
    if not title or not title.strip():
        raise ValueError("Book title is required.")
    if not author or not author.strip() or not category or not category.strip():
        raise ValueError("Author and category are required.")

    if publication_year in ("", None):
        publication_year = None
    else:
        publication_year = int(publication_year)
        if not 1 <= publication_year <= 2100:
            raise ValueError("Enter a valid publication year.")

    connection = get_connection()
    try:
        connection.start_transaction()
        cursor = connection.cursor()
        author_id = _get_or_create_id(
            cursor, "authors", "author_id", "author_name", author
        )
        category_id = _get_or_create_id(
            cursor, "categories", "category_id", "category_name", category
        )
        cursor.execute(
            """
            UPDATE books
            SET title = %s, author_id = %s, category_id = %s,
                publication_year = %s, isbn = %s
            WHERE book_id = %s
            """,
            (title.strip(), author_id, category_id, publication_year,
             isbn.strip() if isbn and isbn.strip() else None, book_id),
        )
        if cursor.rowcount == 0:
            # A rowcount of zero can also mean unchanged values; verify existence.
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if cursor.fetchone() is None:
                raise ValueError("Book was not found.")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def delete_book(book_id):
    """Delete a book that has no loan history."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        if cursor.rowcount == 0:
            raise ValueError("Book was not found.")
        connection.commit()
    except Error:
        connection.rollback()
        raise ValueError(
            "This book cannot be deleted because it has loan history. "
            "Keeping the record protects the library's checkout history."
        )
    finally:
        cursor.close()
        connection.close()


def add_member(first_name, last_name, email):
    """Create a library member and return the new member ID."""
    if not first_name.strip() or not last_name.strip() or not email.strip():
        raise ValueError("First name, last name, and email are required.")
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO members (first_name, last_name, email) VALUES (%s, %s, %s)",
            (first_name.strip(), last_name.strip(), email.strip()),
        )
        member_id = cursor.lastrowid
        connection.commit()
        return member_id
    finally:
        cursor.close()
        connection.close()


def get_members():
    """Return all members, alphabetically."""
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT member_id, first_name, last_name, email "
            "FROM members ORDER BY last_name, first_name"
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def checkout_book(book_id, member_id, loan_days=14):
    """Check out an available book to a member."""
    if not isinstance(loan_days, int) or loan_days < 1:
        raise ValueError("Loan period must be a positive whole number of days.")

    connection = get_connection()
    try:
        connection.start_transaction()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT book_id FROM books WHERE book_id = %s FOR UPDATE",
            (book_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("Book was not found.")

        cursor.execute(
            "SELECT loan_id FROM loans WHERE book_id = %s AND return_date IS NULL",
            (book_id,),
        )
        if cursor.fetchone():
            raise ValueError("This book is already checked out.")

        cursor.execute(
            "SELECT member_id FROM members WHERE member_id = %s",
            (member_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("Member was not found.")

        due_date = date.today() + timedelta(days=loan_days)
        cursor.execute(
            """
            INSERT INTO loans (book_id, member_id, checkout_date, due_date)
            VALUES (%s, %s, %s, %s)
            """,
            (book_id, member_id, datetime.now(), due_date),
        )
        loan_id = cursor.lastrowid
        connection.commit()
        return loan_id
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def return_book(book_id):
    """Close the active loan for a book."""
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE loans
            SET return_date = NOW()
            WHERE book_id = %s AND return_date IS NULL
            """,
            (book_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("This book does not have an active checkout.")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_dashboard_counts():
    """Return total, available, and currently checked-out book counts."""
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM books) AS total_books,
                (SELECT COUNT(*) FROM books b
                 WHERE NOT EXISTS (
                    SELECT 1 FROM loans l
                    WHERE l.book_id = b.book_id AND l.return_date IS NULL
                 )) AS available_books,
                (SELECT COUNT(*) FROM loans WHERE return_date IS NULL)
                    AS checked_out_books
            """
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def search_open_library(title, limit=10):
    """
    Search Open Library by title.
    Returns a list of processed results suitable for displaying in the UI.
    """
    if not title or not title.strip():
        raise ValueError("Enter a title to search.")

    query = urlencode({"title": title.strip(), "limit": limit})
    url = f"https://openlibrary.org/search.json?{query}"
    request = Request(url, headers={"User-Agent": "LibraryManagementCapstone/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Open Library could not be reached: {exc}") from exc

    results = []
    for item in data.get("docs", []):
        authors = item.get("author_name", [])
        results.append({
            "title": item.get("title", "Unknown title"),
            "author": ", ".join(authors) if authors else "Unknown author",
            "publication_year": item.get("first_publish_year"),
            "isbn": item.get("isbn", [None])[0],
            "open_library_key": item.get("key"),
        })
    return results
