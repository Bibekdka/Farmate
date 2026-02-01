import os
import datetime
import requests
import calendar as cal
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
# from flask_migrate import Migrate
from config import config

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
# Load configuration from environment
# FLASK_ENV is deprecated in Flask 2.3+, using APP_ENV instead
config_name = os.environ.get('APP_ENV', 'development')
app.config.from_object(config[config_name])

db = SQLAlchemy(app)

# Weather API Config (from environment variables)
WEATHER_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', 'YOUR_OPENWEATHERMAP_API_KEY')
LAT = os.environ.get('FARM_LATITUDE', '26.1445')
LON = os.environ.get('FARM_LONGITUDE', '91.7362')

# --- DATABASE MODELS (SQL TABLES) ---
class FarmRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    activity_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    expense_type = db.Column(db.String(50))  # Fuel, Labour, Food, Transportation, Misc
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

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    priority = db.Column(db.String(20), default='Normal')
    completed = db.Column(db.Boolean, default=False)

# Initialize Database
with app.app_context():
    db.create_all()

# --- HELPER FUNCTIONS ---
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        forecast = []
        if response.status_code == 200:
            for item in data['list'][0:24:8]:
                day_data = {
                    'date': item['dt_txt'].split(" ")[0],
                    'temp': item['main']['temp'],
                    'desc': item['weather'][0]['description'],
                    'rain_prob': item.get('pop', 0) * 100
                }
                forecast.append(day_data)
        return forecast
    except Exception as e:
        print(f"Weather Error: {e}")
        return []

def convert_to_kg(value, unit):
    conversions = {'kg': 1, 'quintal': 100, 'tons': 1000, 'grams': 0.001}
    return value * conversions.get(unit.lower(), 1)

# --- ROUTES ---
@app.route('/')
def home():
    weather_data = get_weather()
    recent_activities = FarmRecord.query.order_by(FarmRecord.date.desc()).limit(5).all()
    today_reminders = Reminder.query.filter_by(date=datetime.date.today(), completed=False).all()
    return render_template('index.html', weather=weather_data, activities=recent_activities, reminders=today_reminders)

@app.route('/calendar')
def calendar_view():
    now = datetime.date.today()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    cal_matrix = cal.monthcalendar(year, month)
    
    records = FarmRecord.query.filter(
        FarmRecord.date >= datetime.date(year, month, 1),
        FarmRecord.date < datetime.date(year, month, 1) + relativedelta(months=1)
    ).all()
    
    reminders = Reminder.query.filter(
        Reminder.date >= datetime.date(year, month, 1),
        Reminder.date < datetime.date(year, month, 1) + relativedelta(months=1)
    ).all()
    
    events_by_date = {}
    for record in records:
        date_key = record.date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = {'records': [], 'reminders': []}
        events_by_date[date_key]['records'].append(record)
    
    for reminder in reminders:
        date_key = reminder.date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = {'records': [], 'reminders': []}
        events_by_date[date_key]['reminders'].append(reminder)
    
    month_name = cal.month_name[month]
    prev_month = month - 1 if month > 1 else 12
    next_month = month + 1 if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html', cal_matrix=cal_matrix, year=year, month=month,
                          month_name=month_name, events_by_date=events_by_date,
                          prev_month=prev_month, next_month=next_month,
                          prev_year=prev_year, next_year=next_year)

@app.route('/dashboard')
def dashboard():
    records = FarmRecord.query.all()
    total_income = sum(r.amount for r in records if r.category == 'Income')
    total_expense = sum(r.amount for r in records if r.category == 'Expense')
    net_profit = total_income - total_expense
    
    # Expense breakdown by type
    expense_breakdown = {}
    for r in records:
        if r.category == 'Expense' and r.expense_type:
            if r.expense_type not in expense_breakdown:
                expense_breakdown[r.expense_type] = 0
            expense_breakdown[r.expense_type] += r.amount
    
    return render_template('dashboard.html', income=total_income, expense=total_expense, 
                          profit=net_profit, records=records, expense_breakdown=expense_breakdown)

@app.route('/add_record', methods=['POST'])
def add_record():
    date_str = request.form.get('date')
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    new_record = FarmRecord(
        date=date_obj,
        activity_type=request.form.get('activity'),
        category=request.form.get('category'),
        expense_type=request.form.get('expense_type'),
        amount=float(request.form.get('amount')),
        description=request.form.get('desc')
    )
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    record = FarmRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        record.date = date_obj
        record.activity_type = request.form.get('activity')
        record.category = request.form.get('category')
        record.expense_type = request.form.get('expense_type')
        record.amount = float(request.form.get('amount'))
        record.description = request.form.get('desc')
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_record.html', record=record)

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    record = FarmRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/crops', methods=['GET', 'POST'])
def crops():
    if request.method == 'POST':
        crop = Crop(
            crop_name=request.form.get('crop_name'),
            variety=request.form.get('variety'),
            season=request.form.get('season'),
            area=request.form.get('area'),
            sowing_date=datetime.datetime.strptime(request.form.get('sowing_date'), '%Y-%m-%d').date() if request.form.get('sowing_date') else None,
            expected_harvest=datetime.datetime.strptime(request.form.get('expected_harvest'), '%Y-%m-%d').date() if request.form.get('expected_harvest') else None,
            notes=request.form.get('notes')
        )
        db.session.add(crop)
        db.session.commit()
        return redirect(url_for('crops'))
    all_crops = Crop.query.all()
    return render_template('crops.html', crops=all_crops)

@app.route('/edit_crop/<int:crop_id>', methods=['GET', 'POST'])
def edit_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if request.method == 'POST':
        crop.crop_name = request.form.get('crop_name')
        crop.variety = request.form.get('variety')
        crop.season = request.form.get('season')
        crop.area = request.form.get('area')
        crop.sowing_date = datetime.datetime.strptime(request.form.get('sowing_date'), '%Y-%m-%d').date() if request.form.get('sowing_date') else None
        crop.expected_harvest = datetime.datetime.strptime(request.form.get('expected_harvest'), '%Y-%m-%d').date() if request.form.get('expected_harvest') else None
        crop.status = request.form.get('status')
        crop.notes = request.form.get('notes')
        db.session.commit()
        return redirect(url_for('crops'))
    return render_template('edit_crop.html', crop=crop)

@app.route('/delete_crop/<int:crop_id>', methods=['POST'])
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    return redirect(url_for('crops'))

@app.route('/yield', methods=['GET', 'POST'])
def yield_tracking():
    if request.method == 'POST':
        crop_id = request.form.get('crop_id')
        yield_value = float(request.form.get('yield_value'))
        unit = request.form.get('unit')
        yield_in_kg = convert_to_kg(yield_value, unit)
        yield_rec = Yield(
            date=datetime.datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            crop_id=crop_id,
            yield_value=yield_value,
            unit=unit,
            yield_in_kg=yield_in_kg,
            notes=request.form.get('notes')
        )
        db.session.add(yield_rec)
        db.session.commit()
        return redirect(url_for('yield_tracking'))
    crops_list = Crop.query.all()
    yields = Yield.query.all()
    return render_template('yield.html', crops=crops_list, yields=yields)

@app.route('/delete_yield/<int:yield_id>', methods=['POST'])
def delete_yield(yield_id):
    yield_rec = Yield.query.get_or_404(yield_id)
    db.session.delete(yield_rec)
    db.session.commit()
    return redirect(url_for('yield_tracking'))

@app.route('/disease_log', methods=['GET', 'POST'])
def disease_log():
    if request.method == 'POST':
        disease = DiseaseLog(
            date=datetime.datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            crop_id=request.form.get('crop_id'),
            disease_name=request.form.get('disease_name'),
            severity=request.form.get('severity'),
            affected_area=request.form.get('affected_area'),
            treatment=request.form.get('treatment'),
            notes=request.form.get('notes')
        )
        db.session.add(disease)
        db.session.commit()
        return redirect(url_for('disease_log'))
    crops_list = Crop.query.all()
    diseases = DiseaseLog.query.order_by(DiseaseLog.date.desc()).all()
    return render_template('disease_log.html', crops=crops_list, diseases=diseases)

@app.route('/delete_disease/<int:disease_id>', methods=['POST'])
def delete_disease(disease_id):
    disease = DiseaseLog.query.get_or_404(disease_id)
    db.session.delete(disease)
    db.session.commit()
    return redirect(url_for('disease_log'))

@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if request.method == 'POST':
        reminder = Reminder(
            date=datetime.datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            title=request.form.get('title'),
            description=request.form.get('description'),
            priority=request.form.get('priority', 'Normal')
        )
        db.session.add(reminder)
        db.session.commit()
        return redirect(url_for('reminders'))
    all_reminders = Reminder.query.order_by(Reminder.date.asc()).all()
    return render_template('reminders.html', reminders=all_reminders)

@app.route('/complete_reminder/<int:reminder_id>', methods=['POST'])
def complete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    reminder.completed = True
    db.session.commit()
    return redirect(url_for('reminders'))

@app.route('/delete_reminder/<int:reminder_id>', methods=['POST'])
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    return redirect(url_for('reminders'))

@app.route('/reports')
def reports():
    records = FarmRecord.query.all()
    total_income = sum(r.amount for r in records if r.category == 'Income')
    total_expense = sum(r.amount for r in records if r.category == 'Expense')
    net_profit = total_income - total_expense
    
    monthly_data = {}
    for record in records:
        month_key = record.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        if record.category == 'Income':
            monthly_data[month_key]['income'] += record.amount
        else:
            monthly_data[month_key]['expense'] += record.amount
    
    activity_data = {}
    for record in records:
        activity = record.activity_type
        if activity not in activity_data:
            activity_data[activity] = {'income': 0, 'expense': 0}
        if record.category == 'Income':
            activity_data[activity]['income'] += record.amount
        else:
            activity_data[activity]['expense'] += record.amount
    
    yields = Yield.query.all()
    total_yield_kg = sum(y.yield_in_kg or 0 for y in yields)
    diseases = DiseaseLog.query.all()
    disease_count = len(diseases)
    severe_diseases = len([d for d in diseases if d.severity == 'Severe'])
    
    return render_template('reports.html', total_income=total_income, total_expense=total_expense,
                          net_profit=net_profit, monthly_data=monthly_data, activity_data=activity_data,
                          total_yield_kg=total_yield_kg, disease_count=disease_count,
                          severe_diseases=severe_diseases)

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        content = request.form.get('content')
        new_note = Note(content=content)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('notes'))
    all_notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=all_notes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'])
