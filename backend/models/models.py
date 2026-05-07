import datetime
from flask_login import UserMixin
from backend.database import db

class FarmRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    activity_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    expense_type = db.Column(db.String(50))
    amount = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(200))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100))
    season = db.Column(db.String(50))
    area = db.Column(db.String(100))
    sowing_date = db.Column(db.Date)
    expected_harvest = db.Column(db.Date)
    status = db.Column(db.String(50), default='Active')
    notes = db.Column(db.String(500))

class Yield(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    yield_value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    yield_in_kg = db.Column(db.Float)
    notes = db.Column(db.String(200))
    crop = db.relationship('Crop', backref='yields')

class DiseaseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    disease_name = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    affected_area = db.Column(db.String(100))
    treatment = db.Column(db.String(500))
    notes = db.Column(db.String(200))
    crop = db.relationship('Crop', backref='diseases')

class PestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    crop_name = db.Column(db.String(50))
    pest_name = db.Column(db.String(50))
    value = db.Column(db.Float)
    alert_status = db.Column(db.String(20)) # SAFE, ALERT, WARNING
    notes = db.Column(db.String(200))

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.String(20), default='Normal')
    completed = db.Column(db.Boolean, default=False)

class WeatherLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    max_temp = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    description = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    message = db.Column(db.Text)
