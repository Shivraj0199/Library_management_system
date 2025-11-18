# Deploy library management system on local host
The Library Management System is a simple web-based application designed to help manage books in a library.

## Architecture 
* Frontend: HTML + CSS (Bootstrap for layout)
* Backend: Python (Flask)
* Database: MySQL

## Project structure

``` library_project
│
├── app.py
├── requirements.txt
├── schema.sql
│
├── templates
│    ├── layout.html
│    ├── index.html
│    ├── books.html
│    ├── add_book.html
│    ├── edit_book.html
│    ├── members.html
│    ├── add_member.html
│    ├── issue.html
│    └── transactions.html
│
└── static
     └── css
          └── style.css
```

### Step 1 : Check if Python is installed

``` python --version```

``` py --version```

### Step 2 : Open project folder in Powershell/VS Code

``` cd D:\Library_management_project ```

### Step 3 : Create Virtual Environment

* navigate to your project :

```cd D:\Library_management_project```

* then run :

``` python -m venv venv ```

### Step 4 : Activate the virtual environment (Windows)

``` venv\Scripts\activate ```

### Step 5 : Open MySQL Workbench

* Search MySQL Workbench in Start menu
* Open it

### Step 6 : Connect to Your Local MySQL Server

* Local instance MySQL80

* or

* Localhost

Click on it → enter your MySQL password → it connects.

### Step 7 : Create a New SQL File

* Click File → New Query Tab

A blank SQL editor will open.

### Step 8 : Paste Your schema.sql Content

``` -- schema.sql
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
```

### Step 9 : Run the Script

* Click the lightning bolt icon

### Step 10 : Confirm DB Created

* Left side panel → "Schemas"

* Refresh → You will see library_db

### Step 11 : Run the Python backend
Fire the command inside your project directory

``` python app.py ```

### Step 12 : Open the browser and paste the local host IP

``` Running on http://127.0.0.1:5000 ```

---

## Note :

1) Install python software with .exe file to the path ````https://www.python.org/downloads/windows/````
2) Insatll mysql workbench to coonect python (flask) app
