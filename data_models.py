from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author of one or more books.

    Attributes:
        id (integer): primary key, auto-incrementing unique identifier
        name (string): full name of the author (must be unique)
        birth_date (date): birthdate of the author
        date_of_death (date, optional): the author's date of death

        books (Book): one-to-many relationship containing
                      the books the author wrote
    """
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        birth = self.birth_date.year
        death = self.date_of_death.year if self.date_of_death else ""
        lifespan = f"{birth}–{death}" if death else f"{birth}"
        return f"{self.name} ({lifespan})"


class Book(db.Model):
    """
    Represents a books.
    Attributes:
        id (integer): primary key, auto-incrementing unique identifier
        isbn (string): ISBN-number of the book
        title (sting): title of the book
        publication_year (integer): year of the book's first publication
        book_cover_url (string): url to the matching book cover
        author_id (integer): foreignkey, link to author ID in the author table
    """

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    book_cover_url = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author_id={self.author_id})>"

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by {self.author.name}"
