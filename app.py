import os
import datetime
import requests
import calendar as cal
import shutil
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from ai_service import ai_advisor

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
# Load configuration from environment
config_name = os.environ.get('APP_ENV', 'development')
app.config.from_object(config[config_name])

db = SQLAlchemy(app)

import json

# Weather API Config (from environment variables)
LAT = os.environ.get('FARM_LATITUDE', '26.1445')
LON = os.environ.get('FARM_LONGITUDE', '91.7362')

# === AUTO-BACKUP SYSTEM ===
def auto_backup_database():
    """Automatic backup after database changes"""
    try:
        db_path = Path('instance/farm_data.db')
        if not db_path.exists():
            return
        
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'auto_backup_{timestamp}.db'
        shutil.copy2(db_path, backup_path)
        
        # Keep only last 20 auto-backups
        backups = sorted(backup_dir.glob('auto_backup_*.db'), key=lambda x: x.stat().st_mtime, reverse=True)
        for old_backup in backups[20:]:
            old_backup.unlink()
    except Exception as e:
        print(f"Auto-backup warning: {e}")

# Load Knowledge Data
try:
    with open('data/pest_etl.json', 'r') as f:
        PEST_ETL_DB = json.load(f)
    with open('data/pest_calendar.json', 'r') as f:
        PEST_CALENDAR_DB = json.load(f)
    with open('data/crop_calendar.json', 'r') as f:
        CROP_CALENDAR_DB = json.load(f)
    with open('data/turmeric_data.json', 'r') as f:
        TURMERIC_DB = json.load(f)
except Exception as e:
    print(f"Warning: Knowledge Base Load Error - {e}")
    PEST_ETL_DB = []
    PEST_CALENDAR_DB = []
    CROP_CALENDAR_DB = []
    TURMERIC_DB = {}

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

# --- 3. Pest Log Model ---
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



# --- HELPER FUNCTIONS ---
def get_weather_openmeteo():
    try:
        # Open-Meteo URL (No API Key needed)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LAT,
            "longitude": LON,
            "daily": ["weather_code", "temperature_2m_max", "precipitation_sum"],
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # WMO Weather Code Mapping
        wmo_codes = {
            0: "☀️ Clear Sky",
            1: "🌤️ Mainly Clear", 2: "⛅ Partly Cloudy", 3: "☁️ Overcast",
            45: "🌫️ Fog", 48: "🌫️ Rime Fog",
            51: "DRIZZLE: Light", 53: "DRIZZLE: Moderate", 55: "DRIZZLE: Dense",
            61: "Rain: Slight", 63: "RAINING: Moderate", 65: "RAINING: Heavy",
            71: "SNOW: Slight", 73: "SNOW: Moderate", 75: "SNOW: Heavy",
            77: "❄️ Snow Grains",
            80: "SHOWERS: Slight", 81: "SHOWERS: Moderate", 82: "SHOWERS: Violent",
            95: "⚡ Thunderstorm", 96: "⚡ Thunderstorm + Hail", 99: "⚡ Thunderstorm + Heavy Hail"
        }

        forecast = []
        if response.status_code == 200:
            daily = data.get('daily', {})
            # Loop through 7 days
            for i in range(len(daily.get('time', []))):
                code = daily['weather_code'][i]
                desc = wmo_codes.get(code, f"Code: {code}")
                
                day_data = {
                    'date': daily['time'][i],
                    'temp': daily['temperature_2m_max'][i],
                    'desc': desc,
                    'rain_prob': daily['precipitation_sum'][i] # Showing Rain amount in mm
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
    weather_data = get_weather_openmeteo()
    
    # --- AUTO-ARCHIVE WEATHER LOGIC (Lazy Cron) ---
    # Check if we have weather data and haven't logged it for today yet
    if weather_data:
        today = datetime.date.today()
        existing_log = WeatherLog.query.filter_by(date=today).first()
        
        if not existing_log:
            try:
                # weather_data[0] is today's forecast
                todays_weather = weather_data[0]
                new_log = WeatherLog(
                    date=today,
                    max_temp=todays_weather['temp'],
                    rainfall=todays_weather['rain_prob'], # Stored as 'rain_prob' key in our helper, but represents sum in mm
                    description=todays_weather['desc']
                )
                db.session.add(new_log)
                db.session.commit()
                print(f"[SUCCESS] Archived weather for {today}")
            except Exception as e:
                print(f"[ERROR] Failed to archive weather: {e}")
                db.session.rollback()
    
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
            events_by_date[date_key] = {'records': [], 'reminders': [], 'notes': []}
        events_by_date[date_key]['records'].append(record)
    
    for reminder in reminders:
        date_key = reminder.date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = {'records': [], 'reminders': [], 'notes': []}
        events_by_date[date_key]['reminders'].append(reminder)
        
    # FETCH NOTES FOR THIS MONTH
    # Note: SQLite doesn't have extract('month'), so filter by range
    start_date = datetime.date(year, month, 1)
    # End date is start of next month
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)
        
    notes = Note.query.filter(Note.created_at >= start_date, Note.created_at < end_date).all()
    
    for note in notes:
        date_key = note.created_at.day
        if date_key not in events_by_date:
             events_by_date[date_key] = {'records': [], 'reminders': [], 'notes': []}
        events_by_date[date_key]['notes'].append(note)
    
    month_name = cal.month_name[month]
    prev_month = month - 1 if month > 1 else 12
    next_month = month + 1 if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1
    
    return render_template('calendar.html', cal_matrix=cal_matrix, year=year, month=month,
                          month_name=month_name, events_by_date=events_by_date,
                          prev_month=prev_month, next_month=next_month,
                          prev_year=prev_year, next_year=next_year,
                          today=now)

@app.route('/dashboard')
def dashboard():
    # OPTIMIZED: Use SQL Aggregation instead of fetching all records
    total_income = db.session.query(func.sum(FarmRecord.amount)).filter(FarmRecord.category == 'Income').scalar() or 0
    total_expense = db.session.query(func.sum(FarmRecord.amount)).filter(FarmRecord.category == 'Expense').scalar() or 0
    net_profit = total_income - total_expense
    
    # optimize graph data fetching (limit to recent if needed, but for now just all for graph is okay, or aggregate)
    # The template uses 'records' list for the table. We still need that, but maybe limit it?
    # The user didn't ask to pagination, but explicitly mentioned "calculating totals" as the bottleneck.
    # Let's keep fetching records for the table display, but the Math is now fast.
    # If the user has 1000 records, displaying them all in HTML is also slow. 
    # For now, I will keep 'records' query as is to avoid breaking the "Transaction History" table feature, 
    # but the TOP CARDS (totals) which are the most important are now instant.
    
    records = FarmRecord.query.order_by(FarmRecord.date.desc()).all()
    
    # Expense breakdown by type (Also Optimized)
    expense_breakdown_query = db.session.query(
        FarmRecord.expense_type, func.sum(FarmRecord.amount)
    ).filter(
        FarmRecord.category == 'Expense', 
        FarmRecord.expense_type != None
    ).group_by(FarmRecord.expense_type).all()
    
    expense_breakdown = {type_: amount for type_, amount in expense_breakdown_query}
    
    return render_template('dashboard.html', income=total_income, expense=total_expense, 
                          profit=net_profit, records=records, expense_breakdown=expense_breakdown)

@app.route('/weather_history')
def weather_history():
    logs = WeatherLog.query.order_by(WeatherLog.date.desc()).all()
    return render_template('weather_history.html', logs=logs)

@app.route('/daily_log')
def daily_log():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('daily_log.html', notes=notes)

@app.route('/save_daily_log', methods=['POST'])
def save_daily_log():
    content = request.form.get('content')
    date_str = request.form.get('date')
    
    if content:
        created_at = datetime.datetime.now()
        if date_str:
            try:
                created_at = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        note = Note(content=content, created_at=created_at)
        db.session.add(note)
        db.session.commit()
        auto_backup_database()  # Automatic backup
    return redirect(url_for('daily_log'))

@app.route('/quick_note', methods=['POST'])
def quick_note():
    content = request.form.get('content')
    if content:
        note = Note(content=f"📝 Daily Log: {content}")
        db.session.add(note)
        db.session.commit()
    return redirect(url_for('dashboard'))

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

@app.route('/api/financial_data')
def financial_data_api():
    # 1. Monthly Income vs Expense (Last 6 Months)
    today = datetime.date.today()
    months = []
    income_data = []
    expense_data = []
    
    # Needs relativedelta import if not present globally, but it was imported at top
    for i in range(5, -1, -1):
        start_date = (today.replace(day=1) - relativedelta(months=i))
        end_date = start_date + relativedelta(months=1)
        
        month_label = start_date.strftime("%b")
        months.append(month_label)
        
        inc = db.session.query(func.sum(FarmRecord.amount)).filter(
            FarmRecord.date >= start_date,
            FarmRecord.date < end_date,
            FarmRecord.category == 'Income'
        ).scalar() or 0
        income_data.append(inc)
        
        exp = db.session.query(func.sum(FarmRecord.amount)).filter(
            FarmRecord.date >= start_date,
            FarmRecord.date < end_date,
            FarmRecord.category == 'Expense'
        ).scalar() or 0
        expense_data.append(exp)

    # 2. Expense Breakdown (All Time)
    expense_breakdown = db.session.query(
        FarmRecord.expense_type, func.sum(FarmRecord.amount)
    ).filter(
        FarmRecord.category == 'Expense', 
        FarmRecord.expense_type != None
    ).group_by(FarmRecord.expense_type).all()
    
    expense_labels = [item[0] for item in expense_breakdown]
    expense_values = [item[1] for item in expense_breakdown]
    
    return jsonify({
        'months': months,
        'income': income_data,
        'expense': expense_data,
        'expense_labels': expense_labels,
        'expense_values': expense_values
    })

@app.route('/api/analyze_logs', methods=['POST'])
def analyze_logs_api():
    # Fetch last 7 days of logs
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    recent_logs = Note.query.filter(Note.created_at >= one_week_ago).order_by(Note.created_at.asc()).all()
    
    if not recent_logs:
        return jsonify({"status": "error", "message": "No logs found for the last 7 days to analyze."})
        
    # Call AI Service
    result = ai_advisor.analyze_logs(recent_logs)
    return jsonify(result)

@app.route('/api/ask_crop_doctor', methods=['POST'])
def ask_crop_doctor():
    data = request.json
    crop_name = data.get('crop_name')
    sowing_date = data.get('sowing_date')
    
    if not crop_name:
        return jsonify({"status": "error", "message": "Crop name is required"})
        
    result = ai_advisor.ask_crop_doctor(crop_name, sowing_date)
    return jsonify(result)

@app.route('/api/recommend_crops', methods=['POST'])
def recommend_crops_api():
    data = request.json
    area = data.get('area')
    season = data.get('season')
    
    if not area or not season:
        return jsonify({"status": "error", "message": "Area and Season are required"})
        
    result = ai_advisor.recommend_crops(area, season)
    return jsonify(result)

@app.route('/api/diagnose_disease', methods=['POST'])
def diagnose_disease_api():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
        
    try:
        image_bytes = file.read()
        mime_type = file.mimetype or "image/jpeg"
        
        result = ai_advisor.diagnose_from_image(image_bytes, mime_type)
        
        # Ensure result is JSON
        if result.get('status') == 'success':
            import json
            content = result['content']
            # Strip markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            try:
                # Parse string to JSON object
                json_data = json.loads(content)
                return jsonify({"status": "success", "data": json_data})
            except:
                # If parsing fails, return text as is
                return jsonify({"status": "success", "data": {"treatment": content, "disease_name": "AI Diagnosis", "severity": "Check Description"}})
                
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/estimate_duration', methods=['POST'])
def estimate_duration_api():
    data = request.json
    crop_name = data.get('crop_name')
    if not crop_name:
        return jsonify({"status": "error"})
    
    days = ai_advisor.get_crop_duration(crop_name)
    return jsonify({"status": "success", "days": days} if days else {"status": "error"})

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
    
    severe_diseases = len([d for d in diseases if d.severity == 'Severe'])
    
    return render_template('reports.html', total_income=total_income, total_expense=total_expense,
                          net_profit=net_profit, monthly_data=monthly_data, activity_data=activity_data,
                          total_yield_kg=total_yield_kg, disease_count=disease_count,
                          severe_diseases=severe_diseases)

@app.route('/knowledge')
def knowledge_hub():
    return render_template('knowledge.html', 
                          pest_etl=PEST_ETL_DB, 
                          pest_calendar=PEST_CALENDAR_DB, 
                          crop_calendar=CROP_CALENDAR_DB,
                          turmeric_db=TURMERIC_DB)

# --- HELPER: Weather ---
def get_current_weather():
    api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
    if not api_key:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# --- API: Check ETL ---
@app.route('/api/check-etl', methods=['POST'])
def api_check_etl():
    data = request.json
    crop_name = data.get('crop')
    pest_name = data.get('pest')
    current_value = float(data.get('value', 0))
    
    # 1. Database Lookup
    if crop_name not in PEST_ETL_DB:
         return jsonify({"status": "Error", "message": f"Crop '{crop_name}' not found."})
    
    crop_data = PEST_ETL_DB[crop_name]
    if pest_name not in crop_data:
        return jsonify({"status": "Error", "message": f"Pest '{pest_name}' not found for {crop_name}."})
        
    pest_info = crop_data[pest_name]
    threshold = pest_info["threshold"]
    condition = pest_info["condition"]
    unit = pest_info["unit"]
    
    # 2. Logic Check
    is_alert = False
    if condition == "greater_equal" and current_value >= threshold:
        is_alert = True
    elif condition == "greater" and current_value > threshold:
        is_alert = True
        
    # 3. Weather Context (Real-time)
    weather = get_current_weather()
    weather_risk = ""
    if weather:
        temp = weather['main']['temp']
        humidity = weather['main']['humidity']
        # Contextual Logic: Tea Mosquito Bug loves warm & humid
        if pest_name == "Tea Mosquito Bug" and temp > 25 and humidity > 80:
             weather_risk = "Create Pre-warning: Current warm & humid weather favors rapid pest growth."
             if not is_alert and current_value >= (threshold * 0.8):
                 is_alert = True # Lower threshold trigger
                 pest_info["advisory"] += " (Triggered early due to high risk weather)"

    # 4. Historical Trend Check
    # Check if value is increasing
    last_log = PestLog.query.filter_by(crop_name=crop_name, pest_name=pest_name).order_by(PestLog.date.desc()).first()
    trend_msg = ""
    if last_log:
        if current_value > last_log.value:
            trend_msg = f"📈 Trend: Value increased from {last_log.value} since {last_log.date}."
        elif current_value < last_log.value:
            trend_msg = "📉 Trend: Pest population is declining."
            
    # 5. Save to Log
    status_label = "ALERT" if is_alert else "SAFE"
    new_log = PestLog(crop_name=crop_name, pest_name=pest_name, value=current_value, alert_status=status_label, notes=weather_risk)
    db.session.add(new_log)
    db.session.commit()
    
    # 6. Response
    response = {
        "status": status_label,
        "severity": "High" if is_alert else "Low",
        "threshold": threshold,
        "unit": unit,
        "message": f"⚠️ ALERT: {pest_name} ({current_value}) exceeds threshold!" if is_alert else f"✅ Normal: Below limit ({threshold}).",
        "recommendation": pest_info["advisory"] if is_alert else "Continue regular monitoring.",
        "weather_context": weather_risk,
        "trend": trend_msg
    }
    return jsonify(response)

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

@app.route('/edit_note/<int:note_id>', methods=['POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.content = request.form.get('content')
    db.session.commit()
    return redirect(url_for('notes'))

@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('notes'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config['DEBUG'])
