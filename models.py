from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WeatherEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(120), nullable=False)