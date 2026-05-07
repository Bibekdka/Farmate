import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Handle postgres URL format
db_url = os.environ.get('DATABASE_URL', 'sqlite:///public.db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url and db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
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

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

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
    return render_template('cart.html', cart_items=cart_items, total=total)

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
    return render_template('login.html')

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
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def seed_db():
    if Product.query.count() == 0:
        products = [
            Product(name='Organic Turmeric', description='Freshly harvested organic turmeric root.', price=15.99, stock=100),
            Product(name='Farm Fresh Tomatoes', description='Juicy red tomatoes from our greenhouse.', price=4.99, stock=50),
            Product(name='Organic Lettuce', description='Crisp organic lettuce leaves.', price=3.50, stock=30),
            Product(name='Raw Honey', description='Pure, unpasteurized honey from our apiary.', price=24.00, stock=20),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_db()
    app.run(debug=True, port=5000)
