from flask import Flask
from flask import render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///side.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def game():
    users = User.query.all()
    return render_template('game.html', users=users)

@app.route('/user/<name>')
def user_index(name):
    return render_template('game.html', user_name = name)

@app.route('/form', methods=['GET', 'POST'])
def user_form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256')
        user = User(name=name, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('game'))
        except:
            return "Помилка при реєстрації"

    return render_template('form.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('game'))
        else:
            flash("Невірний email або пароль", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('game'))

if __name__ == "__main__":
   app.run()

