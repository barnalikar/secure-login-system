from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_email = db.Column(db.String(100))

    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))
    device = db.Column(db.String(50))
    ip_address = db.Column(db.String(100))

    login_time = db.Column(db.String(100))