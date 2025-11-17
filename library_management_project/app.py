# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # optional: can store DB creds in .env

app = Flask(__name__)
app.secret_key = 'dev-secret-key'  # in production use secure secret

# MySQL connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', ''),
        database=os.getenv('DB_NAME', 'library_db'),
        auth_plugin='mysql_native_password'
    )

# Home
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    total_books = cursor.fetchone()['total_books']
    cursor.execute("SELECT COUNT(*) as total_members FROM members")
    total_members = cursor.fetchone()['total_members']
    cursor.execute("SELECT COUNT(*) as issued_books FROM transactions WHERE status='issued'")
    issued_books = cursor.fetchone()['issued_books']
    cursor.close()
    conn.close()
    return render_template('index.html', total_books=total_books, total_members=total_members, issued_books=issued_books)

# ---------------- Books CRUD ----------------
@app.route('/books')
def books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY id DESC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['GET','POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        year = request.form.get('year') or None
        copies = request.form.get('copies') or 1

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, publisher, year, copies) VALUES (%s,%s,%s,%s,%s)",
            (title, author, publisher, year, copies)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))

    return render_template('add_book.html')

@app.route('/books/edit/<int:id>', methods=['GET','POST'])
def edit_book(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        year = request.form.get('year') or None
        copies = request.form.get('copies') or 1
        cursor.execute(
            "UPDATE books SET title=%s, author=%s, publisher=%s, year=%s, copies=%s WHERE id=%s",
            (title, author, publisher, year, copies, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))

    cursor.execute("SELECT * FROM books WHERE id=%s", (id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('books'))
    return render_template('edit_book.html', book=book)

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Book deleted', 'info')
    return redirect(url_for('books'))

# ---------------- Members ----------------
@app.route('/members')
def members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members ORDER BY id DESC")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['GET','POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email')
        phone = request.form.get('phone')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name,email,phone) VALUES (%s,%s,%s)", (name,email,phone))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Member added', 'success')
        return redirect(url_for('members'))
    return render_template('add_member.html')

# ---------------- Issue / Return ----------------
@app.route('/issue', methods=['GET','POST'])
def issue():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        issue_date = request.form.get('issue_date') or date.today().isoformat()
        due_days = int(request.form.get('due_days', 14))
        due_date = (date.fromisoformat(issue_date) + timedelta(days=due_days)).isoformat()

        # check copies available
        cursor.execute("SELECT copies FROM books WHERE id=%s", (book_id,))
        b = cursor.fetchone()
        if not b or b['copies'] <= 0:
            flash('No copies available for this book', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('issue'))

        # reduce copies by 1
        cursor.execute("UPDATE books SET copies = copies - 1 WHERE id=%s", (book_id,))
        cursor.execute("INSERT INTO transactions (book_id, member_id, issue_date, due_date, status) VALUES (%s,%s,%s,%s,'issued')",
                       (book_id, member_id, issue_date, due_date))
        conn.commit()
        flash('Book issued successfully', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('transactions'))

    # GET: show available books and members
    cursor.execute("SELECT id, title, copies FROM books WHERE copies > 0")
    books = cursor.fetchall()
    cursor.execute("SELECT id, name FROM members")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('issue.html', books=books, members=members)

@app.route('/return/<int:trans_id>', methods=['POST'])
def return_book(trans_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE id=%s", (trans_id,))
    trans = cursor.fetchone()
    if not trans:
        flash('Transaction not found', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('transactions'))

    if trans['status'] == 'returned':
        flash('Book already returned', 'info')
        cursor.close()
        conn.close()
        return redirect(url_for('transactions'))

    # mark returned
    today = date.today().isoformat()
    cursor.execute("UPDATE transactions SET status='returned', return_date=%s WHERE id=%s", (today, trans_id))
    # increment book copies
    cursor.execute("UPDATE books SET copies = copies + 1 WHERE id=%s", (trans['book_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Book returned successfully', 'success')
    return redirect(url_for('transactions'))

@app.route('/transactions')
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT t.*, b.title as book_title, m.name as member_name
           FROM transactions t
           JOIN books b ON t.book_id = b.id
           JOIN members m ON t.member_id = m.id
           ORDER BY t.id DESC"""
    )
    tx = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('transactions.html', transactions=tx)

# --------------- Search example (simple) ----------------
@app.route('/search')
def search():
    q = request.args.get('q','').strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if q:
        like = f"%{q}%"
        cursor.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", (like, like))
        results = cursor.fetchall()
    else:
        results = []
    cursor.close()
    conn.close()
    return render_template('books.html', books=results)

if __name__ == '__main__':
    app.run(debug=True)
