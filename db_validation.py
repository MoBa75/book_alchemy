import os
import sys
from sqlalchemy import inspect
from data_models import db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'library.sqlite')

def validate_database(app):
    if not os.path.isfile(DB_DIR):
        print('Database not found. Please run db_creation.py to create the database.')
        sys.exit(1)
    with app.app_context():
        inspector = inspect(db.engine)
        expected_tables = {
                            'authors': {'id', 'name', 'birth_date', 'date_of_death'},
                            'books': {'id', 'isbn', 'title', 'publication_year',
                                      'book_cover_url', 'author_id'}
                            }
        actual_tables = set(inspector.get_table_names())
        missing_tables = set(expected_tables.keys()) - actual_tables
        if missing_tables:
            print(f'Missing tables: {', '.join(missing_tables)}')
            print('Please correct or delete the database and rerun db_creation.py')
            sys.exit(1)

        for table, expected_cols in expected_tables.items():
            actual_cols = {col['name'] for col in inspector.get_columns(table)}
            if expected_cols != actual_cols:
                print(f"Table '{table}' has incorrect columns.")
                print(f"Expected: {expected_cols}")
                print(f"Found: {actual_cols}")
                print('Please correct or delete the database and rerun db_creation.py')
                sys.exit(1)
    print("Database validated successfully")