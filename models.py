from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the database instance
db = SQLAlchemy()

# User model with additional fields: name, username, email, dob, phone, and password
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    # Define the columns for the User model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Full Name
    username = db.Column(db.String(150), unique=True, nullable=False)  # Username (must be unique)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Email ID (must be unique)
    dob = db.Column(db.String(10), nullable=False)  # Date of Birth
    phone = db.Column(db.String(10), nullable=False)  # Phone Number (10 digits)
    password = db.Column(db.String(150), nullable=False)  # Password (hashed for security)

    def __repr__(self):
        return f'<User {self.username}>'
