from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user_model
from flask import flash
import pprint

db = 'users_jokes'

class Joke:
    db_name = 'jokes'
    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.question = data['question']
        self.punchline = data['punchline']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users = None

    @classmethod
    def save(cls,data):
        query = "INSERT INTO jokes (title, question, punchline, user_id) VALUES (%(title)s,%(question)s,%(punchline)s,%(user_id)s);"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM jokes JOIN users on users.id = jokes.user_id;"
        results =  connectToMySQL(db).query_db(query)
        all_jokes = []
        for row in results:
            joke = cls(row)
            user_data = {
                'id': row['users.id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'password': row['password'],
                'created_at': row['users.created_at'],
                'updated_at': row['users.updated_at']
            }
            joke.users = user_model.User(user_data)
            all_jokes.append(joke)
        return all_jokes
    
    @classmethod
    def get_one_joke_by_user(cls, id):
        query = 'SELECT * FROM jokes JOIN users on users.id = jokes.user_id WHERE jokes.id = %(joke)s;'
        results = connectToMySQL(db).query_db(query,{'joke':id})
        pprint.pprint(results,sort_dicts=False)
        joke = cls(results[0])
        user_data = {
            'id': results[0]['users.id'],
            'first_name': results[0]['first_name'],
            'last_name': results[0]['last_name'],
            'email': results[0]['email'],
            'password': results[0]['password'],
            'created_at': results[0]['users.created_at'],
            'updated_at': results[0]['users.updated_at']
        }
        joke.users = user_model.User(user_data)
        return joke
    
    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM jokes WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query,data)
        return cls( results[0] )

    @classmethod
    def update(cls, data):
        query = "UPDATE jokes SET title=%(title)s, question=%(question)s, punchline=%(punchline)s,updated_at=NOW() WHERE id = %(id)s;"
        return connectToMySQL(db).query_db(query,data)
    
    @classmethod
    def destroy(cls,data):
        query = "DELETE FROM jokes WHERE id = %(id)s;"
        return connectToMySQL(db).query_db(query,data)

    @staticmethod
    def validate_joke(joke):
        is_valid = True
        if joke['title'] <= str(0):
            is_valid = False
            flash("Title cannot be blank.", "joke")
        if len(joke['punchline']) == 0:
            is_valid = False
            flash("Punchline/One-liner field cannot be blank.","joke")
        return is_valid