from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from models import db, Section, User
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freshcart.db'
app.config['SECRET_KEY'] = 'freshcart-secret'
db.init_app(app)

@app.route('/')
def home():
    sections = Section.query.all()
    return render_template('home.html', sections=sections)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please Login In First")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

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