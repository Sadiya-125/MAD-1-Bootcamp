from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from models import db, Section, User, Products
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freshcart.db'
app.config['SECRET_KEY'] = 'freshcart-secret'
db.init_app(app)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please Login In First")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    sections = Section.query.all()
    return render_template('home.html', sections=sections)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Admins Only!")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/admin') # READ
@admin_required
def admin_dashboard():
    sections = Section.query.all()
    return render_template('admin_dashboard.html', sections=sections)

@app.route('/section/add', methods=['GET', 'POST']) # CREATE
@admin_required
def add_section():
    if request.method == 'POST':
        db.session.add(Section(name=request.form['name'], description=request.form['description']))
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_section.html')

@app.route('/section/edit/<int:id>', methods=['GET', 'POST']) # UPDATE
@admin_required
def edit_section(id):
    section = Section.query.get_or_404(id)
    if request.method == 'POST':
        section.name = request.form['name']
        section.description = request.form['description']

        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_section.html', section=section)

@app.route('/section/delete/<int:id>') # DELETE
@admin_required
def delete_section(id):
    db.session.delete(Section.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/section/<int:section_id>/product/add', methods=['GET', 'POST']) # CREATE
@admin_required
def add_product(section_id):
    section = Section.query.get_or_404(section_id)
    if request.method == 'POST':
        db.session.add(Products(name=request.form['name'], price=float(request.form['price']), units=request.form['units'], stock=request.form['stock'], section_id=section.id))
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_product.html', section=section)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST']) # UPDATE
@admin_required
def edit_product(id):
    product = Products.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.units = request.form['units']
        product.stock = int(request.form['stock'])

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product)

@app.route('/product/delete/<int:id>') # DELETE
@admin_required
def delete_product(id):
    db.session.delete(Products.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    results = (Products.query.filter(Products.name.ilike(f'%{q}%')).all() if q else [])
    return render_template('search.html', results=results, query=q)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Username Already Exists")
            return redirect(url_for('register'))

        db.session.add(User(username=username, password=generate_password_hash(password)))

        db.session.commit()
        flash("Registration Successful. Please Login.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('home'))
        
        flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Seed the Database
def init_db():
     with app.app_context():
        db.create_all() # instance/freshcart.db

        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123'), is_admin=True))
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)