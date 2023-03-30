from flask import render_template,redirect,session,request, flash
from flask_app import app
from flask_app.models.joke_model import Joke
from flask_app.models.user_model import User

@app.route('/create/joke')
def new_joke():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id":session['user_id']
    }
    return render_template('new_joke.html',user=User.get_by_id(data))


@app.route('/create/joke',methods=['POST'])
def create_joke():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Joke.validate_joke(request.form):
        return redirect('/create/joke')
    data = {
        "title": request.form["title"],
        "question": request.form["question"],
        "punchline": request.form["punchline"],
        "user_id": session["user_id"]
    }
    Joke.save(data)
    return redirect('/dashboard')

@app.route('/edit/joke/<int:id>')
def edit_joke(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id":id
    }
    user_data = {
        "id":session['user_id']
    }
    return render_template("edit_joke.html",joke=Joke.get_one(data),user=User.get_by_id(user_data))

@app.route('/update/joke/<int:id>',methods=['POST'])
def update_joke(id):
    if 'user_id' not in session:
        return redirect('/logout')
    if not Joke.validate_joke(request.form):
        return redirect('/create/joke')
    data = {
        "title": request.form["title"],
        "question": request.form["question"],
        "punchline": request.form["punchline"],
        "id": id
    }
    Joke.update(data)
    return redirect('/dashboard')

@app.route('/joke/<int:id>')
def view_joke(id):
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template("view_joke.html",joke=Joke.get_one_joke_by_user(id))

@app.route('/destroy/joke/<int:id>')
def destroy_joke(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id":id
    }
    Joke.destroy(data)
    return redirect('/dashboard')