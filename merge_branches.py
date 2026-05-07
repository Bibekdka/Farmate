"""
Merge script: Updates app.py to have:
- Public routes at / (shop, cart, login, register, etc.)
- Admin routes at /admin/ (dashboard, calendar, crops, etc.)
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Add Flask-Login imports after existing imports
# ============================================================
old_imports = "from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file"
new_imports = """from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash"""
content = content.replace(old_imports, new_imports)

# ============================================================
# 2. Add Flask-Login setup after migrate = Migrate(app, db)
# ============================================================
old_migrate = "migrate = Migrate(app, db)"
new_migrate = """migrate = Migrate(app, db)

# Flask-Login setup for public website
login_manager = LoginManager(app)
login_manager.login_view = 'login'"""
content = content.replace(old_migrate, new_migrate)

# ============================================================
# 3. Add public website models after existing models (before HELPER FUNCTIONS)
# ============================================================
public_models = '''
# --- PUBLIC WEBSITE MODELS ---
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''

content = content.replace(
    "# --- HELPER FUNCTIONS ---",
    public_models + "# --- HELPER FUNCTIONS ---"
)

# ============================================================
# 4. Prefix ALL admin routes with /admin and rename functions
# ============================================================
# Route replacements: (old_route, new_route, old_func, new_func)
route_replacements = [
    ("@app.route('/')", "@app.route('/admin')\n@app.route('/admin/')", "def home()", "def admin_home()"),
    ("@app.route('/calendar')", "@app.route('/admin/calendar')", "def calendar_view()", "def admin_calendar_view()"),
    ("@app.route('/dashboard')", "@app.route('/admin/dashboard')", "def dashboard()", "def admin_dashboard()"),
    ("@app.route('/weather_history')", "@app.route('/admin/weather_history')", "def weather_history()", "def admin_weather_history()"),
    ("@app.route('/daily_log')", "@app.route('/admin/daily_log')", "def daily_log()", "def admin_daily_log()"),
    ("@app.route('/save_daily_log', methods=['POST'])", "@app.route('/admin/save_daily_log', methods=['POST'])", "def save_daily_log()", "def admin_save_daily_log()"),
    ("@app.route('/quick_note', methods=['POST'])", "@app.route('/admin/quick_note', methods=['POST'])", "def quick_note()", "def admin_quick_note()"),
    ("@app.route('/add_record', methods=['POST'])", "@app.route('/admin/add_record', methods=['POST'])", "def add_record()", "def admin_add_record()"),
    ("@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])", "@app.route('/admin/edit_record/<int:record_id>', methods=['GET', 'POST'])", "def edit_record(record_id)", "def admin_edit_record(record_id)"),
    ("@app.route('/delete_record/<int:record_id>', methods=['POST'])", "@app.route('/admin/delete_record/<int:record_id>', methods=['POST'])", "def delete_record(record_id)", "def admin_delete_record(record_id)"),
    ("@app.route('/crops', methods=['GET', 'POST'])", "@app.route('/admin/crops', methods=['GET', 'POST'])", "def crops()", "def admin_crops()"),
    ("@app.route('/edit_crop/<int:crop_id>', methods=['GET', 'POST'])", "@app.route('/admin/edit_crop/<int:crop_id>', methods=['GET', 'POST'])", "def edit_crop(crop_id)", "def admin_edit_crop(crop_id)"),
    ("@app.route('/delete_crop/<int:crop_id>', methods=['POST'])", "@app.route('/admin/delete_crop/<int:crop_id>', methods=['POST'])", "def delete_crop(crop_id)", "def admin_delete_crop(crop_id)"),
    ("@app.route('/yield', methods=['GET', 'POST'])", "@app.route('/admin/yield', methods=['GET', 'POST'])", "def yield_tracking()", "def admin_yield_tracking()"),
    ("@app.route('/delete_yield/<int:yield_id>', methods=['POST'])", "@app.route('/admin/delete_yield/<int:yield_id>', methods=['POST'])", "def delete_yield(yield_id)", "def admin_delete_yield(yield_id)"),
    ("@app.route('/api/financial_data')", "@app.route('/admin/api/financial_data')", "def financial_data_api()", "def admin_financial_data_api()"),
    ("@app.route('/api/analyze_logs', methods=['POST'])", "@app.route('/admin/api/analyze_logs', methods=['POST'])", "def analyze_logs_api()", "def admin_analyze_logs_api()"),
    ("@app.route('/api/ask_crop_doctor', methods=['POST'])", "@app.route('/admin/api/ask_crop_doctor', methods=['POST'])", "def ask_crop_doctor()", "def admin_ask_crop_doctor()"),
    ("@app.route('/api/recommend_crops', methods=['POST'])", "@app.route('/admin/api/recommend_crops', methods=['POST'])", "def recommend_crops_api()", "def admin_recommend_crops_api()"),
    ("@app.route('/api/diagnose_disease', methods=['POST'])", "@app.route('/admin/api/diagnose_disease', methods=['POST'])", "def diagnose_disease_api()", "def admin_diagnose_disease_api()"),
    ("@app.route('/api/estimate_duration', methods=['POST'])", "@app.route('/admin/api/estimate_duration', methods=['POST'])", "def estimate_duration_api()", "def admin_estimate_duration_api()"),
    ("@app.route('/disease_log', methods=['GET', 'POST'])", "@app.route('/admin/disease_log', methods=['GET', 'POST'])", "def disease_log()", "def admin_disease_log()"),
    ("@app.route('/delete_disease/<int:disease_id>', methods=['POST'])", "@app.route('/admin/delete_disease/<int:disease_id>', methods=['POST'])", "def delete_disease(disease_id)", "def admin_delete_disease(disease_id)"),
    ("@app.route('/reminders', methods=['GET', 'POST'])", "@app.route('/admin/reminders', methods=['GET', 'POST'])", "def reminders()", "def admin_reminders()"),
    ("@app.route('/complete_reminder/<int:reminder_id>', methods=['POST'])", "@app.route('/admin/complete_reminder/<int:reminder_id>', methods=['POST'])", "def complete_reminder(reminder_id)", "def admin_complete_reminder(reminder_id)"),
    ("@app.route('/delete_reminder/<int:reminder_id>', methods=['POST'])", "@app.route('/admin/delete_reminder/<int:reminder_id>', methods=['POST'])", "def delete_reminder(reminder_id)", "def admin_delete_reminder(reminder_id)"),
    ("@app.route('/reports')", "@app.route('/admin/reports')", "def reports()", "def admin_reports()"),
    ("@app.route('/knowledge')", "@app.route('/admin/knowledge')", "def knowledge_hub()", "def admin_knowledge_hub()"),
    ("@app.route('/api/check-etl', methods=['POST'])", "@app.route('/admin/api/check-etl', methods=['POST'])", "def api_check_etl()", "def admin_api_check_etl()"),
    ("@app.route('/notes', methods=['GET', 'POST'])", "@app.route('/admin/notes', methods=['GET', 'POST'])", "def notes()", "def admin_notes()"),
    ("@app.route('/edit_note/<int:note_id>', methods=['POST'])", "@app.route('/admin/edit_note/<int:note_id>', methods=['POST'])", "def edit_note(note_id)", "def admin_edit_note(note_id)"),
    ("@app.route('/delete_note/<int:note_id>', methods=['POST'])", "@app.route('/admin/delete_note/<int:note_id>', methods=['POST'])", "def delete_note(note_id)", "def admin_delete_note(note_id)"),
    ("@app.route('/api/backup_status')", "@app.route('/admin/api/backup_status')", "def backup_status_api()", "def admin_backup_status_api()"),
    ("@app.route('/api/run_backup', methods=['POST'])", "@app.route('/admin/api/run_backup', methods=['POST'])", "def run_manual_backup()", "def admin_run_manual_backup()"),
    ("@app.route('/download_export')", "@app.route('/admin/download_export')", "def download_export()", "def admin_download_export()"),
    ("@app.route('/api/add_historical_weather', methods=['POST'])", "@app.route('/admin/api/add_historical_weather', methods=['POST'])", "def run_add_historical_weather()", "def admin_run_add_historical_weather()"),
]

for old_route, new_route, old_func, new_func in route_replacements:
    content = content.replace(old_route, new_route)
    content = content.replace(old_func, new_func)

# ============================================================
# 5. Fix url_for references inside admin route functions
# ============================================================
# These are url_for('old_name') -> url_for('admin_old_name')
url_for_replacements = {
    "url_for('home')": "url_for('admin_home')",
    "url_for('dashboard')": "url_for('admin_dashboard')",
    "url_for('calendar_view')": "url_for('admin_calendar_view')",
    "url_for('daily_log')": "url_for('admin_daily_log')",
    "url_for('save_daily_log')": "url_for('admin_save_daily_log')",
    "url_for('quick_note')": "url_for('admin_quick_note')",
    "url_for('add_record')": "url_for('admin_add_record')",
    "url_for('crops')": "url_for('admin_crops')",
    "url_for('yield_tracking')": "url_for('admin_yield_tracking')",
    "url_for('disease_log')": "url_for('admin_disease_log')",
    "url_for('reminders')": "url_for('admin_reminders')",
    "url_for('notes')": "url_for('admin_notes')",
    "url_for('reports')": "url_for('admin_reports')",
    "url_for('knowledge_hub')": "url_for('admin_knowledge_hub')",
}
for old_url, new_url in url_for_replacements.items():
    content = content.replace(old_url, new_url)

# ============================================================
# 6. Fix render_template calls in admin routes to use admin/ prefix
# ============================================================
admin_templates = [
    'index.html', 'calendar.html', 'crops.html', 'daily_log.html',
    'dashboard.html', 'disease_log.html', 'edit_crop.html', 'edit_record.html',
    'knowledge.html', 'notes.html', 'reminders.html', 'reports.html',
    'weather_history.html', 'yield.html'
]
for tmpl in admin_templates:
    content = content.replace(f"render_template('{tmpl}'", f"render_template('admin/{tmpl}'")

# ============================================================
# 7. Add public website routes before the if __name__ block
# ============================================================
public_routes = '''
# ============================================================
# --- PUBLIC WEBSITE ROUTES (Organics-O-Eats) ---
# ============================================================

@app.route('/')
def index():
    """Public homepage."""
    return render_template('public/index.html')

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('public/shop.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    session.modified = True
    flash('Item added to cart!', 'success')
    return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            cart_items.append({'product': product, 'quantity': quantity, 'total': item_total})
    return render_template('public/cart.html', cart_items=cart_items, total=total)

@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))
    total = 0
    for p_id, qty in cart.items():
        p = Product.query.get(int(p_id))
        if p: total += p.price * qty
    order = Order(user_id=current_user.id, total_amount=total)
    db.session.add(order)
    db.session.commit()
    session.pop('cart', None)
    flash('Order placed successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/schedule_visit', methods=['POST'])
def schedule_visit():
    name = request.form.get('name')
    email = request.form.get('email')
    date_str = request.form.get('date')
    message = request.form.get('message')
    try:
        visit_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        visit = Visit(name=name, email=email, date=visit_date, message=message)
        db.session.add(visit)
        db.session.commit()
        flash('Visit scheduled successfully! We will contact you soon.', 'success')
    except Exception as e:
        flash('Error scheduling visit. Please try again.', 'error')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('public/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'error')
            return redirect(url_for('register'))
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    return render_template('public/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def seed_products():
    """Seed default products if none exist."""
    if Product.query.count() == 0:
        products = [
            Product(name='Organic Turmeric', description='Freshly harvested organic turmeric root.', price=15.99, stock=100),
            Product(name='Farm Fresh Tomatoes', description='Juicy red tomatoes from our greenhouse.', price=4.99, stock=50),
            Product(name='Organic Lettuce', description='Crisp organic lettuce leaves.', price=3.50, stock=30),
            Product(name='Raw Honey', description='Pure, unpasteurized honey from our apiary.', price=24.00, stock=20),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Seeded default products.")

'''

content = content.replace(
    "if __name__ == '__main__':",
    public_routes + "if __name__ == '__main__':"
)

# ============================================================
# 8. Update the __main__ block to also seed products
# ============================================================
content = content.replace(
    "    with app.app_context():\n        db.create_all()\n    app.run(debug=True)",
    "    with app.app_context():\n        db.create_all()\n        seed_products()\n    app.run(debug=True, port=5000)"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: app.py has been merged!")
print("- Public routes at /")
print("- Admin routes at /admin/")
