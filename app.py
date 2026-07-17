from flask import Flask, render_template
from models import db, Section

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///freshcart.db'
app.config['SECRET_KEY'] = 'freshcart-secret'
db.init_app(app)

@app.route('/')
def home():
    sections = Section.query.all()
    return render_template('home.html', sections=sections)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # instance/freshcart.db
    app.run(debug=True, port=8080)