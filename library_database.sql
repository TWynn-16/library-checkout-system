-- Library Management System: database setup and sample data
-- Run this script in MySQL Workbench.
-- It creates five related tables and demonstrates PKs, FKs, constraints, and 3NF.

CREATE DATABASE IF NOT EXISTS library_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE library_management;

CREATE TABLE IF NOT EXISTS authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(150) NOT NULL,
    CONSTRAINT uq_authors_name UNIQUE (author_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(80) NOT NULL,
    CONSTRAINT uq_categories_name UNIQUE (category_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INT NOT NULL,
    category_id INT NOT NULL,
    publication_year SMALLINT NULL,
    isbn VARCHAR(20) NULL,
    CONSTRAINT fk_books_author
        FOREIGN KEY (author_id) REFERENCES authors(author_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_books_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_books_isbn UNIQUE (isbn),
    CONSTRAINT chk_books_publication_year
        CHECK (publication_year IS NULL OR publication_year BETWEEN 1 AND 2100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    CONSTRAINT uq_members_email UNIQUE (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    checkout_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    return_date DATETIME NULL,
    CONSTRAINT fk_loans_book
        FOREIGN KEY (book_id) REFERENCES books(book_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_loans_member
        FOREIGN KEY (member_id) REFERENCES members(member_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX ix_loans_book_return (book_id, return_date),
    INDEX ix_loans_member (member_id)
) ENGINE=InnoDB;

-- Sample authors and categories
INSERT IGNORE INTO authors (author_name) VALUES
('J.R.R. Tolkien'),
('H.P. Lovecraft'),
('Edgar Allan Poe'),
('Stephen King'),
('Alex Michaelides');

INSERT IGNORE INTO categories (category_name) VALUES
('Fantasy'),
('Horror'),
('Poetry'),
('Thriller');

-- Sample books
INSERT INTO books (title, author_id, category_id, publication_year, isbn)
SELECT 'The Lord of the Rings', a.author_id, c.category_id, 1954, NULL
FROM authors a JOIN categories c
WHERE a.author_name = 'J.R.R. Tolkien' AND c.category_name = 'Fantasy'
AND NOT EXISTS (SELECT 1 FROM books WHERE title = 'The Lord of the Rings');

INSERT INTO books (title, author_id, category_id, publication_year, isbn)
SELECT 'The Call of Cthulhu', a.author_id, c.category_id, 1928, NULL
FROM authors a JOIN categories c
WHERE a.author_name = 'H.P. Lovecraft' AND c.category_name = 'Horror'
AND NOT EXISTS (SELECT 1 FROM books WHERE title = 'The Call of Cthulhu');

INSERT INTO books (title, author_id, category_id, publication_year, isbn)
SELECT 'The Complete Poems of Edgar Allan Poe', a.author_id, c.category_id, NULL, NULL
FROM authors a JOIN categories c
WHERE a.author_name = 'Edgar Allan Poe' AND c.category_name = 'Poetry'
AND NOT EXISTS (SELECT 1 FROM books WHERE title = 'The Complete Poems of Edgar Allan Poe');

INSERT INTO books (title, author_id, category_id, publication_year, isbn)
SELECT 'IT', a.author_id, c.category_id, 1986, NULL
FROM authors a JOIN categories c
WHERE a.author_name = 'Stephen King' AND c.category_name = 'Horror'
AND NOT EXISTS (SELECT 1 FROM books WHERE title = 'IT');

INSERT INTO books (title, author_id, category_id, publication_year, isbn)
SELECT 'The Silent Patient', a.author_id, c.category_id, 2019, NULL
FROM authors a JOIN categories c
WHERE a.author_name = 'Alex Michaelides' AND c.category_name = 'Thriller'
AND NOT EXISTS (SELECT 1 FROM books WHERE title = 'The Silent Patient');

-- Sample members
INSERT IGNORE INTO members (first_name, last_name, email) VALUES
('Jordan', 'Smith', 'jordan.smith@example.com'),
('Taylor', 'Brown', 'taylor.brown@example.com'),
('Morgan', 'Davis', 'morgan.davis@example.com');

-- Five meaningful retrieval queries (plus one additional query)

-- 1. List books with author, category, and current availability.
SELECT b.book_id, b.title, a.author_name, c.category_name,
       CASE
           WHEN EXISTS (
               SELECT 1 FROM loans l
               WHERE l.book_id = b.book_id AND l.return_date IS NULL
           ) THEN 'Checked Out'
           ELSE 'Available'
       END AS current_status
FROM books b
JOIN authors a ON b.author_id = a.author_id
JOIN categories c ON b.category_id = c.category_id
ORDER BY b.title;

-- 2. Count how many books are in each category.
SELECT c.category_name, COUNT(b.book_id) AS book_count
FROM categories c
LEFT JOIN books b ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
ORDER BY book_count DESC, c.category_name;

-- 3. Show members and how many total loans they have made.
SELECT m.member_id, m.first_name, m.last_name,
       COUNT(l.loan_id) AS total_loans
FROM members m
LEFT JOIN loans l ON m.member_id = l.member_id
GROUP BY m.member_id, m.first_name, m.last_name
ORDER BY total_loans DESC, m.last_name;

-- 4. Find books that have never been checked out.
SELECT b.book_id, b.title, a.author_name
FROM books b
JOIN authors a ON b.author_id = a.author_id
LEFT JOIN loans l ON b.book_id = l.book_id
WHERE l.loan_id IS NULL
ORDER BY b.title;

-- 5. Find currently overdue books and the members who borrowed them.
SELECT b.title, m.first_name, m.last_name, l.checkout_date, l.due_date
FROM loans l
JOIN books b ON l.book_id = b.book_id
JOIN members m ON l.member_id = m.member_id
WHERE l.return_date IS NULL
  AND l.due_date < CURRENT_DATE
ORDER BY l.due_date;

-- 6. Average number of days books are kept, using completed loans.
SELECT AVG(DATEDIFF(DATE(l.return_date), DATE(l.checkout_date)))
       AS average_days_borrowed
FROM loans l
WHERE l.return_date IS NOT NULL;

-- Examples of data manipulation (run separately when needed):
-- UPDATE books SET title = 'Updated Book Title' WHERE book_id = 1;
-- DELETE FROM books WHERE book_id = 1;
-- The DELETE will be rejected if the book has loan history, preserving referential integrity.
