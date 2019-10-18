CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE users_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    rating INTEGER NOT NULL,
    user_text VARCHAR,
    user_id INTEGER REFERENCES users_table (id),
    books_id INTEGER REFERENCES books (id)
);
