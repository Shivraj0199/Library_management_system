-- schema.sql
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- books table
CREATE TABLE IF NOT EXISTS books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255),
  publisher VARCHAR(255),
  year INT,
  copies INT DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- members table
CREATE TABLE IF NOT EXISTS members (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- transactions (issue/return)
CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT NOT NULL,
  member_id INT NOT NULL,
  issue_date DATE NOT NULL,
  due_date DATE,
  return_date DATE DEFAULT NULL,
  status ENUM('issued','returned') DEFAULT 'issued',
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
  FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- sample data
INSERT INTO books (title, author, publisher, year, copies)
VALUES ('Introduction to Algorithms', 'Cormen', 'MIT Press', 2009, 3),
       ('Clean Code', 'Robert C. Martin', 'Prentice Hall', 2008, 2),
       ('Python Crash Course', 'Eric Matthes', 'No Starch Press', 2019, 4);

INSERT INTO members (name, email, phone)
VALUES ('Amit Sharma','amit@example.com','9876543210'),
       ('Reena Patil','reena@example.com','9123456780');
