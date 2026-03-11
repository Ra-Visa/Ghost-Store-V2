import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ghost-store-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ghost_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model with color fields
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    text_color = db.Column(db.String(50), default='#ffffff')  # Text color
    price_color = db.Column(db.String(50), default='#00ff00')  # Green price by default
    card_bg_color = db.Column(db.String(50), default='#2c3034')  # Card background
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

# Create database tables
with app.app_context():
    db.create_all()
    # Add sample products if database is empty
    if Product.query.count() == 0:
        sample_products = [
            Product(
                name="NETFLIX",
                price=0.10,
                image_url="https://i.ibb.co/CsXf3S0C/Chat-GPT-Image-Mar-11-2026-03-42-51-PM.png",
                description="NETFLIX COOKIE - Login Cookie in Chrome or Firefox",
                text_color="#ffffff",
                price_color="#00ff00",  # Green price
                card_bg_color="#1a1d20"
            ),
            Product(
                name="NETFLIX PREMIUM",
                price=0.25,
                image_url="https://i.ibb.co/CsXf3S0C/Chat-GPT-Image-Mar-11-2026-03-42-51-PM.png",
                description="NETFLIX PREMIUM COOKIE - 4K Ultra HD Available",
                text_color="#ffffff",
                price_color="#00ff00",  # Green price
                card_bg_color="#1a1d20"
            ),
            Product(
                name="NETFLIX 1 MONTH",
                price=0.50,
                image_url="https://i.ibb.co/CsXf3S0C/Chat-GPT-Image-Mar-11-2026-03-42-51-PM.png",
                description="NETFLIX 1 MONTH SUBSCRIPTION - Premium Account",
                text_color="#ffffff",
                price_color="#00ff00",  # Green price
                card_bg_color="#1a1d20"
            ),
            Product(
                name="NETFLIX FAMILY",
                price=0.75,
                image_url="https://i.ibb.co/CsXf3S0C/Chat-GPT-Image-Mar-11-2026-03-42-51-PM.png",
                description="NETFLIX FAMILY PLAN - 4 Screens Simultaneously",
                text_color="#ffffff",
                price_color="#00ff00",  # Green price
                card_bg_color="#1a1d20"
            )
        ]
        db.session.bulk_save_objects(sample_products)
        db.session.commit()

# Login decorator
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'Ghost' and password == 'Ghost1122':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        description = request.form.get('description')
        text_color = request.form.get('text_color', '#ffffff')
        price_color = request.form.get('price_color', '#00ff00')
        card_bg_color = request.form.get('card_bg_color', '#2c3034')
        
        new_product = Product(
            name=name,
            price=float(price),
            image_url=image_url,
            description=description,
            text_color=text_color,
            price_color=price_color,
            card_bg_color=card_bg_color
        )
        
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit.html', product=None)

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.image_url = request.form.get('image_url')
        product.description = request.form.get('description')
        product.text_color = request.form.get('text_color', '#ffffff')
        product.price_color = request.form.get('price_color', '#00ff00')
        product.card_bg_color = request.form.get('card_bg_color', '#2c3034')
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit.html', product=product)

@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)