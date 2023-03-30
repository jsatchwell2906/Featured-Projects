from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import joke_model
import re
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$')

db = 'users_jokes'

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        if 'photo' in data:
            self.photo = data['photo']
        else:
            self.photo = None
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.jokes = []

    @classmethod
    def save(cls,data):
        query = "INSERT INTO users (first_name,last_name,email,password) VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s)"
        return connectToMySQL(db).query_db(query,data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(db).query_db(query)
        users = []
        for row in results:
            users.append( cls(row))
        return users

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query,data)
        return cls(results[0])
    
    @classmethod
    def get_users_with_jokes(cls):
        query = 'SELECT * FROM users JOIN jokes on users.id = jokes.user_id;'
        results = connectToMySQL(db).query_db(query)
        users = []
        for row in results:
            if len(users) == 0:
                users.append(cls(row))
            else:
                last_user = users[len(users) - 1]
                if last_user.id != row['id']:
                    users.append(cls(row))
            last_user = users[len(users) - 1]
            joke_data = {
                'id': row['jokes.id'],
                'title': row['title'],
                'question': row['question'],
                'punchline': row['punchline'],
                'user_id': row['user_id'],
                'created_at': row['jokes.created_at'],
                'updated_at': row['jokes.updated_at']
            }
            last_user.jokes.append(joke_model.Joke(joke_data))
        return users


    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(db).query_db(query,user)
        if len(results) >= 1:
            flash("Email already exists.","register")
            is_valid=False
        if not EMAIL_REGEX.match(user['email']):
            flash("Please enter a valid email.","register")
            is_valid=False
        if len(user['first_name']) < 2:
            flash("First name must be at least 2 characters.","register")
            is_valid= False
        if len(user['last_name']) < 2:
            flash("Last name must be at least 2 characters.","register")
            is_valid= False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters with minimum one uppercase, one number and one special character.","register")
            is_valid= False
        if user['password'] != user['confirm']:
            flash("Passwords do not match.","register")
        return is_valid
    
    @classmethod
    def upload_photo(cls, file):
        if file.filename == '':
            return False

        if '.' not in file.filename or \
            file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return False

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

        return filename

    @classmethod
    def update_photo(cls, user_id, photo_path):
        query = "UPDATE users SET photo = %(photo)s WHERE id = %(user_id)s;"
        data = {
            'user_id': user_id,
            'photo': photo_path
        }
        return connectToMySQL(db).query_db(query, data)


