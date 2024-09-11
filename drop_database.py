import os
from models import db
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Path to your SQLite database file
db_path = 'users.db'

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("Dropped all tables.")

    # Delete the SQLite database file
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted database file: {db_path}")
    else:
        print(f"No database file found at {db_path}.")
