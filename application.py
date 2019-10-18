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

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL_PROJECT1"))
db = scoped_session(sessionmaker(bind=engine))


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

    # type_s = db.execute(
    #     'SELECT id FROM users_table WHERE name = :username',
    #     {'username': username}
    # ).first().id
    # return render_template('index.html', message=type_s)
    # check_it = (db.execute('SELECT id FROM users_table WHERE name = :username AND password_hash = :password',
    #                        {'username': username, 'password': password}).rowcount != 0)
    # return render_template('index.html', message=check_it)

    if (
            db.execute(
            'SELECT id FROM users_table WHERE name = :username AND password_hash = :password',
            {'username': username, 'password': password}).rowcount != 0):

        session['user_id'] = db.execute('SELECT id FROM users_table WHERE name = :username',
                                        {'username': username}).first().id
        session['logged_in'] = True
        # return render_template('index.html', message='Successfully logged in')
        return redirect(url_for('index'))
    else:
        return render_template('error.html', message='Invalid password or username')

    # if password == check_password[0]:
    #     session['user_id'] = db.execute(
    #         'SELECT id FROM users_table WHERE name = :username',
    #         {'username': username}
    #     )
    #     session['logged_in'] = True
    #     return render_template('index.html', message='Successfully logged in')
    # else:
    #     return render_template('error.html', message='Invalid password or username')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session['logged_in'] = False
    return redirect(url_for('index'))
