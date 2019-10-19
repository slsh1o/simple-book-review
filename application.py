import os

from flask import (
    Flask, session, render_template, request,
    redirect, url_for)
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL_PROJECT1"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("GOODREADS_API_KEY"):
    raise RuntimeError("GOODREADS_API_KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL_PROJECT1"))
db = scoped_session(sessionmaker(bind=engine))

# Set goodreads api key
goodreas_api_key = os.getenv("GOODREADS_API_KEY")


@app.route("/")
def index():
    if session['logged_in']:
        username = db.execute('SELECT name FROM users_table WHERE id = :user_id',
                              {'user_id': session.get('user_id')}).first().name
        message = f'Welcome, {username}'
    else:
        message = 'Welcome to bReview website'
    return render_template('index.html', message=message)


@app.route('/signup')
def signup():
    return render_template('register.html')


@app.route('/register_user', methods=['POST'])
def register_user():
    username = request.form.get('username')
    password = request.form.get('user_password')

    db.execute(
        'INSERT INTO users_table (name, password_hash) VALUES (:name, :password_hash)',
        {'name': username, 'password_hash': password}
    )
    db.commit()

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('user_password')

    if (
            db.execute(
            'SELECT id FROM users_table WHERE name = :username AND password_hash = :password',
            {'username': username, 'password': password}).rowcount != 0):

        session['user_id'] = db.execute('SELECT id FROM users_table WHERE name = :username',
                                        {'username': username}).first().id
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return render_template('error.html', message='Invalid password or username')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/search/')
def search():
    search_query = request.args.get('search_query')

    book = db.execute(
        'SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author',
        {'isbn': search_query, 'title': search_query, 'author': search_query}
    ).first()

    if book is not None and book:
        return render_template('books.html', books=book)
    else:
        search_query = '%' + search_query + '%'
        books = db.execute(
            'SELECT * FROM books WHERE \
            isbn LIKE :isbn OR title LIKE :title OR author LIKE :author',
            {'isbn': search_query, 'title': search_query, 'author': search_query}
        ).fetchall()
        return render_template('books.html', books=books)


@app.route('/book/<int:book_id>')
def book(book_id):
    r_book = db.execute(
        'SELECT isbn, title, author, year FROM books WHERE id = :id',
        {'id': book_id}
    ).first()
    return render_template('book.html', book=r_book)
