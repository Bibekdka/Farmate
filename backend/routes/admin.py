from flask import Blueprint, render_template, jsonify
from sqlalchemy import func
from backend.models.models import FarmRecord, Reminder, WeatherLog
from backend.database import db
import datetime

admin_routes = Blueprint('admin_routes', __name__, template_folder='../../templates')

@admin_routes.route('/')
@admin_routes.route('/admin')
@admin_routes.route('/admin/')
@admin_routes.route('/admin_dashboard')
def admin_home():
    recent_activities = FarmRecord.query.order_by(FarmRecord.date.desc()).limit(5).all()
    today_reminders = Reminder.query.filter_by(date=datetime.date.today(), completed=False).all()
    # For now, placeholder for weather
    return render_template('admin/index.html', weather=[], activities=recent_activities, reminders=today_reminders)

@admin_routes.route('/admin/dashboard')
def admin_dashboard():
    total_income = db.session.query(func.sum(FarmRecord.amount)).filter(FarmRecord.category == 'Income').scalar() or 0
    total_expense = db.session.query(func.sum(FarmRecord.amount)).filter(FarmRecord.category == 'Expense').scalar() or 0
    net_profit = total_income - total_expense
    
    records = FarmRecord.query.order_by(FarmRecord.date.desc()).all()
    
    expense_breakdown_query = db.session.query(
        FarmRecord.expense_type, func.sum(FarmRecord.amount)
    ).filter(
        FarmRecord.category == 'Expense', 
        FarmRecord.expense_type != None
    ).group_by(FarmRecord.expense_type).all()
    
    expense_breakdown = {type_: amount for type_, amount in expense_breakdown_query}
    
    return render_template('admin/dashboard.html', income=total_income, expense=total_expense, 
                          profit=net_profit, records=records, expense_breakdown=expense_breakdown)

@admin_routes.route('/admin/api/financial_data')
def admin_financial_data_api():
    # Basic data structure for the charts
    return jsonify({
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'income': [0, 0, 0, 0, 0, 0],
        'expense': [0, 0, 0, 0, 0, 0],
        'expense_labels': [],
        'expense_values': []
    })
