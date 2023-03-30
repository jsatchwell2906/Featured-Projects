from flask import render_template, redirect, session, request, flash, send_from_directory
from flask_app import app
from flask_app.models.user_model import User
from flask_app.models.joke_model import Joke
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('register.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if not User.validate_register(request.form):
        return redirect('/')
    
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password']).decode('utf-8'),
        "photo": None
    }
    id = User.save(data)
    session['user_id'] = id

    return redirect('/dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    user = User.get_by_email(request.form)

    if not user:
        flash("Login Email and/or Password is incorrect.", "login")
        return redirect('/login')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Login Email and/or Password is incorrect.", "login")
        return redirect('/login')
    session['user_id'] = user.id
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        'id': session['user_id']
    }
    user = User.get_by_id(data)
    print(user.photo)
    print(os.path.abspath(app.config['UPLOAD_FOLDER']))
    return render_template("dashboard.html", user=user.__dict__, jokes=Joke.get_all())



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/add_photo')
def add_photo():
    user = User.get_by_id({'id': session['user_id']})
    session['profile_picture'] = user.photo or 'default.png'
    return render_template('add_photo.html')


@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    file = request.files['file']
    if not file:
        flash('No file uploaded', 'error')
        return redirect('/add_photo')

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    user_id = session['user_id']
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace("\\", "/"))

    user = User.get_by_id({'id': user_id})
    user.photo = photo_path

    try:
        User.update_photo(user_id, filename)
    except FileNotFoundError:
        os.remove(filepath)
        flash('Failed to update profile picture', 'error')
        return redirect('/dashboard')

    session['profile_picture'] = user.photo or 'default_profile_picture.jpg'

    flash('File uploaded successfully', 'success')
    return redirect('/dashboard')



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/static/<filename>')
def uploaded_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
