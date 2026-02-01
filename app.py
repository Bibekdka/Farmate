import os
import datetime
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION ---
# Database Setup (SQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Weather API Config (Replace with your actual API Key)
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
# Set your farm's location (Example: Guwahati, Assam)
LAT = "26.1445"
LON = "91.7362"

# --- DATABASE MODELS (SQL TABLES) ---
class FarmRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    activity_type = db.Column(db.String(50)) # e.g., 'Sowing', 'Fertilizing', 'Harvest', 'Sales'
    category = db.Column(db.String(50))      # e.g., 'Expense', 'Income'
    amount = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(200))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

# Initialize Database
with app.app_context():
    db.create_all()

# --- HELPER FUNCTIONS ---
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        # Parse logic to get today and next few days (simplified)
        forecast = []
        if response.status_code == 200:
            for item in data['list'][0:24:8]: # Get roughly one data point per day (every 8th 3-hour segment)
                day_data = {
                    'date': item['dt_txt'].split(" ")[0],
                    'temp': item['main']['temp'],
                    'desc': item['weather'][0]['description'],
                    'rain_prob': item.get('pop', 0) * 100 # Probability of precipitation %
                }
                forecast.append(day_data)
        return forecast
    except Exception as e:
        print(f"Weather Error: {e}")
        return []

# --- ROUTES ---

@app.route('/')
def home():
    # Feature 1: Weather
    weather_data = get_weather()
    
    # Feature 3: Recent Activity Snippet
    recent_activities = FarmRecord.query.order_by(FarmRecord.date.desc()).limit(5).all()
    
    return render_template('index.html', weather=weather_data, activities=recent_activities)

@app.route('/dashboard')
def dashboard():
    # Feature 2: Profit/Loss Dashboard
    records = FarmRecord.query.all()
    
    total_income = sum(r.amount for r in records if r.category == 'Income')
    total_expense = sum(r.amount for r in records if r.category == 'Expense')
    net_profit = total_income - total_expense
    
    # Prepare data for charts
    dates = [r.date.strftime('%Y-%m-%d') for r in records]
    
    return render_template('dashboard.html', 
                           income=total_income, 
                           expense=total_expense, 
                           profit=net_profit,
                           records=records)

@app.route('/add_record', methods=['POST'])
def add_record():
    # Feature 3: Record Activity & Expense
    date_str = request.form.get('date')
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    new_record = FarmRecord(
        date=date_obj,
        activity_type=request.form.get('activity'),
        category=request.form.get('category'), # Expense or Income
        amount=float(request.form.get('amount')),
        description=request.form.get('desc')
    )
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    # Feature 4: Notes
    if request.method == 'POST':
        content = request.form.get('content')
        new_note = Note(content=content)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('notes'))
    
    all_notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=all_notes)

if __name__ == '__main__':
    app.run(debug=True)