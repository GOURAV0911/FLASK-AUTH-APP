import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__, instance_relative_config=True)

# ==============================
# CONFIGURATION
# ==============================

# Secret key from environment (Render) or fallback for local
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key")

# Database (Render will provide DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    'sqlite:///' + os.path.join(app.instance_path, 'users.db')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==============================
# USER MODEL
# ==============================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)


# ==============================
# CREATE DATABASE
# ==============================

with app.app_context():
    db.create_all()


# ==============================
# ROUTES
# ==============================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("All fields are required!")
            return render_template('register.html', name=name, email=email)

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!")
            return render_template('register.html', name=name, email=email)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['email'] = user.email
            session['user_name'] = user.name
            return redirect('/dashboard')
        else:
            flash("Invalid email or password!")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'email' not in session:
        return redirect('/login')

    user = User.query.filter_by(email=session['email']).first()

    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect('/')


# ==============================
# RUN APP (IMPORTANT FOR RENDER)
# ==============================

if __name__ == "__main__":
    app.run(debug=True)