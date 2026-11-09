
-- ============================================
-- Library Checkout System
-- Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS library_checkout;

USE library_checkout;


-- ============================================
-- 1. AUTHORS
-- Stores author information
-- ============================================

CREATE TABLE IF NOT EXISTS Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(100) NOT NULL
);


-- ============================================
-- 2. PUBLISHERS
-- Stores publisher information
-- ============================================

CREATE TABLE IF NOT EXISTS Publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(150) NOT NULL
);


-- ============================================
-- 3. CATEGORIES
-- Stores book categories
-- ============================================

CREATE TABLE IF NOT EXISTS Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);


-- ============================================
-- 4. BOOKS
-- Stores book information
-- ============================================

CREATE TABLE IF NOT EXISTS Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publication_year SMALLINT UNSIGNED,
    publisher_id INT,

    CONSTRAINT fk_books_publisher
        FOREIGN KEY (publisher_id)
        REFERENCES Publishers(publisher_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


-- ============================================
-- 5. BOOK_AUTHORS
-- Connects books with their authors
-- Many-to-many relationship
-- ============================================

CREATE TABLE IF NOT EXISTS Book_Authors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,

    PRIMARY KEY (book_id, author_id),

    CONSTRAINT fk_book_authors_book
        FOREIGN KEY (book_id)
        REFERENCES Books(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_book_authors_author
        FOREIGN KEY (author_id)
        REFERENCES Authors(author_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ============================================
-- 6. BOOK_CATEGORIES
-- Connects books with their categories
-- Many-to-many relationship
-- ============================================

CREATE TABLE IF NOT EXISTS Book_Categories (
    book_id INT NOT NULL,
    category_id INT NOT NULL,

    PRIMARY KEY (book_id, category_id),

    CONSTRAINT fk_book_categories_book
        FOREIGN KEY (book_id)
        REFERENCES Books(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_book_categories_category
        FOREIGN KEY (category_id)
        REFERENCES Categories(category_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ============================================
-- 7. MEMBERS
-- Stores library member information
-- ============================================

CREATE TABLE IF NOT EXISTS Members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),

    membership_status ENUM('Active', 'Inactive')
        NOT NULL DEFAULT 'Active',

    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 8. BOOK_COPIES
-- Tracks individual physical copies
-- ============================================

CREATE TABLE IF NOT EXISTS Book_Copies (
    copy_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    barcode VARCHAR(50) NOT NULL UNIQUE,

    condition_status ENUM('Good', 'Damaged', 'Lost')
        NOT NULL DEFAULT 'Good',

    acquired_on DATE,

    CONSTRAINT fk_book_copies_book
        FOREIGN KEY (book_id)
        REFERENCES Books(book_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- ============================================
-- 9. LOANS
-- Tracks book checkouts and returns
-- ============================================

CREATE TABLE IF NOT EXISTS Loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    copy_id INT NOT NULL,
    member_id INT NOT NULL,
    checkout_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_at DATETIME NOT NULL,
    returned_at DATETIME,

    FOREIGN KEY (copy_id)
        REFERENCES Book_Copies(copy_id),

    FOREIGN KEY (member_id)
        REFERENCES Members(member_id)

) ENGINE=InnoDB;


-- ============================================
-- END OF DATABASE SCHEMA
-- ============================================
