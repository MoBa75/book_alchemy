import os
from flask import Flask
from data_models import db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

os.makedirs(DATA_DIR, exist_ok=True)

DB_DIR = os.path.join(DATA_DIR, 'library.sqlite')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_DIR}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print('Database and tables created successfully')