from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from datetime import datetime
import os


app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'library.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')  # Standard: nach Titel sortieren

    if sort_by == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.order_by(Book.title).all()

    return render_template('home.html', books=books, sort_by=sort_by)



@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = ""
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate_str = request.form.get('birthdate')
        deathdate_str = request.form.get('date_of_death')

        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date() if birthdate_str else None
        deathdate = datetime.strptime(deathdate_str, "%Y-%m-%d").date() if deathdate_str else None

        new_author = Author(name=name, birth_date=birthdate, date_of_death=deathdate)
        db.session.add(new_author)
        db.session.commit()
        message = f"Author '{name}' was successfully added."

    return render_template("add_author.html", message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = ""
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not (title and isbn and publication_year and author_id):
            message = "Please fill in all fields."
        else:
            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year),
                author_id=int(author_id)
            )
            db.session.add(new_book)
            db.session.commit()
            message = f"Book '{title}' was successfully added."

    return render_template("add_book.html", authors=authors, message=message)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)