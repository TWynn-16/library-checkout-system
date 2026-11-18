
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

# Library Management System
# Front-end created using Python and Tkinter.

# Five starter books for the library
books = [
    {
        "id": 1,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    },
    {
        "id": 2,
        "title": "The Call of Cthulhu",
        "author": "H.P. Lovecraft",
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    },
    {
        "id": 3,
        "title": "The Complete Poems of Edgar Allan Poe",
        "author": "Edgar Allan Poe",
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    },
    {
        "id": 4,
        "title": "IT",
        "author": "Stephen King",
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    },
    {
        "id": 5,
        "title": "The Silent Patient",
        "author": "Alex Michaelides",
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    }
]

# Create the main application window
root = tk.Tk()
root.title("Library Management System")
root.geometry("1050x650")
root.configure(bg="#f1f4f8")

# Header
header = tk.Frame(root, bg="#243b55", height=85)
header.pack(fill="x")

tk.Label(
    header,
    text="LIBRARY MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#243b55"
).pack(pady=22)

# Dashboard information
dashboard = tk.Frame(root, bg="#f1f4f8")
dashboard.pack(fill="x", padx=20, pady=15)

total_label = tk.Label(
    dashboard,
    font=("Arial", 12, "bold"),
    bg="#f1f4f8"
)
total_label.pack(side="left", padx=15)

available_label = tk.Label(
    dashboard,
    font=("Arial", 12, "bold"),
    bg="#f1f4f8"
)
available_label.pack(side="left", padx=15)

checked_label = tk.Label(
    dashboard,
    font=("Arial", 12, "bold"),
    bg="#f1f4f8"
)
checked_label.pack(side="left", padx=15)

# Search section
search_frame = tk.Frame(root, bg="#f1f4f8")
search_frame.pack(fill="x", padx=20, pady=10)

tk.Label(
    search_frame,
    text="Search Books:",
    font=("Arial", 11, "bold"),
    bg="#f1f4f8"
).pack(side="left")

search_entry = tk.Entry(
    search_frame,
    width=35,
    font=("Arial", 11)
)
search_entry.pack(side="left", padx=10)

# Book list
table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = (
    "ID", "Title", "Author", "Status",
    "Borrower", "Checkout Date", "Due Date"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    tree.heading(column, text=column)
    tree.column(column, width=135, anchor="center")

tree.column("ID", width=45)
tree.column("Title", width=160)
tree.column("Borrower", width=120)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# Determine the current status of a book
def get_status(book):
    if not book["borrower"]:
        return "Available"

    due_date = datetime.strptime(
        book["due"], "%m/%d/%Y"
    )

    if due_date.date() < datetime.now().date():
        return "Overdue"

    return "Checked Out"


# Update the book list and dashboard
def refresh_books():
    tree.delete(*tree.get_children())

    search = search_entry.get().lower()

    for book in books:
        status = get_status(book)
        book["status"] = status

        # Search by title or author
        searchable = (
            book["title"] + book["author"]
        ).lower()

        if search in searchable:
            tree.insert(
                "",
                "end",
                values=(
                    book["id"],
                    book["title"],
                    book["author"],
                    status,
                    book["borrower"],
                    book["checkout"],
                    book["due"]
                )
            )

    total_label.config(
        text=f"Total Books: {len(books)}"
    )

    available = sum(
        1 for book in books
        if not book["borrower"]
    )

    checked = len(books) - available

    available_label.config(
        text=f"Available: {available}"
    )

    checked_label.config(
        text=f"Checked Out: {checked}"
    )


# Get the selected book
def selected_book():
    selection = tree.selection()

    if not selection:
        messagebox.showwarning(
            "Selection Required",
            "Please select a book first."
        )
        return None

    book_id = int(
        tree.item(selection[0])["values"][0]
    )

    for book in books:
        if book["id"] == book_id:
            return book

    return None


# Add a new book
def add_book():
    title = simpledialog.askstring(
        "Add Book", "Enter book title:"
    )

    if not title or not title.strip():
        return

    author = simpledialog.askstring(
        "Add Book", "Enter author:"
    )

    if not author or not author.strip():
        return

    # Create a new book record
    new_book = {
        "id": max((b["id"] for b in books), default=0) + 1,
        "title": title.strip(),
        "author": author.strip(),
        "status": "Available",
        "borrower": "",
        "checkout": "",
        "due": ""
    }

    books.append(new_book)

    messagebox.showinfo(
        "Success",
        "Book added successfully!"
    )

    refresh_books()


# Edit an existing book
def edit_book():
    book = selected_book()

    if book is None:
        return

    if book["borrower"]:
        messagebox.showwarning(
            "Book Checked Out",
            "Return this book before editing it."
        )
        return

    title = simpledialog.askstring(
        "Edit Book",
        "Enter new title:",
        initialvalue=book["title"]
    )

    if not title or not title.strip():
        return

    author = simpledialog.askstring(
        "Edit Book",
        "Enter new author:",
        initialvalue=book["author"]
    )

    if not author or not author.strip():
        return

    book["title"] = title.strip()
    book["author"] = author.strip()

    messagebox.showinfo(
        "Success",
        "Book updated successfully!"
    )

    refresh_books()


# Delete a book
def delete_book():
    book = selected_book()

    if book is None:
        return

    if book["borrower"]:
        messagebox.showwarning(
            "Book Checked Out",
            "Return the book before deleting it."
        )
        return

    confirm = messagebox.askyesno(
        "Delete Book",
        "Are you sure you want to delete this book?"
    )

    if confirm:
        books.remove(book)

        refresh_books()

        messagebox.showinfo(
            "Success",
            "Book deleted successfully!"
        )


# Check out a book to a library member
def checkout_book():
    book = selected_book()

    if book is None:
        return

    if book["borrower"]:
        messagebox.showwarning(
            "Unavailable",
            "This book is already checked out."
        )
        return

    member = simpledialog.askstring(
        "Book Checkout",
        "Enter the member's name:"
    )

    if not member or not member.strip():
        return

    # Record checkout date and exact time
    now = datetime.now()

    book["borrower"] = member.strip()

    book["checkout"] = now.strftime(
        "%m/%d/%Y %I:%M %p"
    )

    # Set the due date to 14 days later
    book["due"] = (
        now + timedelta(days=14)
    ).strftime("%m/%d/%Y")

    refresh_books()

    messagebox.showinfo(
        "Success",
        f"Book checked out to {member}!\n"
        f"Due date: {book['due']}"
    )


# Return a checked-out book
def return_book():
    book = selected_book()

    if book is None:
        return

    if not book["borrower"]:
        messagebox.showwarning(
            "Not Checked Out",
            "This book is already available."
        )
        return

    member = book["borrower"]

    book["borrower"] = ""
    book["checkout"] = ""
    book["due"] = ""

    refresh_books()

    messagebox.showinfo(
        "Book Returned",
        f"Book returned successfully!\nMember: {member}"
    )


# Sort books alphabetically by title
def sort_books():
    books.sort(
        key=lambda book: book["title"].lower()
    )

    refresh_books()


# Buttons section
button_frame = tk.Frame(root, bg="#f1f4f8")
button_frame.pack(fill="x", padx=20, pady=15)

buttons = [
    ("Add Book", add_book),
    ("Edit Book", edit_book),
    ("Delete Book", delete_book),
    ("Check Out", checkout_book),
    ("Return Book", return_book),
    ("Sort A-Z", sort_books)
]

for text, command in buttons:
    tk.Button(
        button_frame,
        text=text,
        command=command,
        font=("Arial", 10, "bold"),
        bg="#243b55",
        fg="white",
        activebackground="#456b91",
        activeforeground="white",
        width=14,
        pady=8
    ).pack(side="left", padx=5)

# Automatically update the list when searching
search_entry.bind(
    "<KeyRelease>",
    lambda event: refresh_books()
)

# Display books when the program starts
refresh_books()

# Keep the application running
root.mainloop()