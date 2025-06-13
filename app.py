from flask import Flask, render_template, request, redirect, url_for, jsonify
from services.get_bookcover import get_cover_by_isbn
from db_validation import validate_database
from sqlalchemy.exc import SQLAlchemyError
from data_models import db, Author, Book
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func
from datetime import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data',
                                                                    'library.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

validate_database(app)


def add_element(element):
    """
    Adds and commits a file to the database, handles
    errors and rollbacks session in case of error.
    :param element: the element to save in the database,
                    Book or Author class instance
    :return: empty string if successful, else an error message
    """
    try:
        db.session.add(element)
        db.session.commit()
        return ""
    except SQLAlchemyError as error:
        db.session.rollback()
        return f"Database error: {str(error)}"
    except Exception as error:
        db.session.rollback()
        return f"An unexpected error occurred: {str(error)}"


@app.route('/')
def home():
    """
    Shows all books from the table. Gives the possibility to sort the books by
    title or author and furthermore the possibility to search by book title or
    by the name of an author.
    """
    sort_by = request.args.get('sort_by', 'title')
    search = request.args.get('search', '').strip()
    message = request.args.get('message')

    query = Book.query.join(Author)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(or_(Book.title.ilike(search_pattern),
                                 Author.name.ilike(search_pattern)))

    if sort_by == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    return render_template('home.html', books=books,
                           sort_by=sort_by, message=message)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Adds a new author, handles errors and prevents duplicate entries."""
    message = ""
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate = request.form.get('birthdate')
        death_date = request.form.get('date_of_death')

        if not name:
            return jsonify({'error': 'Name is required.'}), 400
        if not birthdate:
            return jsonify({'error': 'Birthdate (yyyy-mm-dd) is required.'}), 400

        try:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'error': 'Birthdate needs to have the format yyyy-mm-dd.'}), 400

        if death_date:
            try:
                death_date = datetime.strptime(death_date, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({'error': 'Date of death needs to have the format yyyy-mm-dd.'}), 400
        else:
            death_date = None

        try:
            check_author = Author.query.filter(
                func.lower(Author.name) == name.strip().lower()).first()
            if check_author:
                return render_template('add_author.html',
                                       message='Author already exists')
            new_author = Author(
                name=name,
                birth_date=birthdate,
                date_of_death=death_date)
            message = add_element(new_author)
            if not message:
                message = f"Author '{name}' was successfully added."
        except ValueError:
            return jsonify({"error": "Invalid data type provided. "
                                     "Please check birthdate and date of death."}), 400
        except SQLAlchemyError as error:
            return jsonify({'error': f'Database query failed: {error}'})
    return render_template("add_author.html", message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Adds a new book, handles errors and prevents duplicate entries."""
    message = ""

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        missing_fields = [variable for variable
                          in ['title', 'isbn', 'publication_year', 'author_id']
                          if not locals()[variable]]
        if missing_fields:
            return jsonify({'error': 'Sorry, something went wrong while processing your request. '
                                     'Please try again in a few moments.'}), 400

        try:
            author_id = int(author_id)
            check_book = Book.query.filter(func.lower(Book.title) == title.strip().lower(),
                                           Book.author_id == author_id).first()
            if check_book:
                return render_template('add_book.html',
                                       message='Book already exists')
            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year),
                book_cover_url=get_cover_by_isbn(isbn),
                author_id=author_id)
            message = add_element(new_book)
            if not message:
                message = f"Book '{title}' was successfully added."
        except ValueError:
            return jsonify({"error": "Invalid data type provided. "
                                     "Please check the year and author ID."}), 400
        except SQLAlchemyError as error:
            return jsonify({'error': f'Database query failed: {error}'})

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors, message=message)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Deletes the selected book."""
    try:
        book = Book.query.options(joinedload(Book.author)).get_or_404(book_id)
        author = book.author

        db.session.delete(book)
        db.session.commit()

        remaining_books = Book.query.filter_by(author_id=author.id).count()

        if remaining_books == 0:
            return redirect(url_for('confirm_author_deletion',
                                    author_id=author.id, message="book_deleted"))
        message = 'Book deleted successfully'

    except SQLAlchemyError as error:
        db.session.rollback()
        message = f'Database error: {error}'

    except Exception as error:
        db.session.rollback()
        message = f'Unexpected error: {error}'
    return redirect(url_for('home', message=message))


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """Deletes an author if there are no more books by the author."""
    try:
        author = Author.query.get_or_404(author_id)

        if Book.query.filter_by(author_id=author.id).count() == 0:
            db.session.delete(author)
            db.session.commit()
            message = "Author deleted successfully"
        else:
            message = "Author not deleted"
    except SQLAlchemyError as error:
        db.session.rollback()
        message = f'Database error: {error}'

    except Exception as error:
        db.session.rollback()
        message = f'Unexpected error: {error}'
    return redirect(url_for('home', message=message))


@app.route('/author/<int:author_id>/confirm_delete')
def confirm_author_deletion(author_id):
    """Asks the user whether the author should also be deleted."""
    try:
        author = Author.query.get_or_404(author_id)
        message = request.args.get("message")
        return render_template('confirm_author_delete.html',
                               author=author, message=message)
    except SQLAlchemyError as error:
        db.session.rollback()
        message = f'Database error: {error}'

    except Exception as error:
        db.session.rollback()
        message = f'Unexpected error: {error}'
    return redirect(url_for('home', message=message))


@app.errorhandler(404)
def not_found(error):
    """Error handling of error 404."""
    return render_template('404.html', error=error), 404


if __name__ == '__main__':
    app.run(port=5002, debug=True)
