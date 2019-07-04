from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from wtforms_forms import *
from models import UserModel
from passlib.hash import pbkdf2_sha512
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from time import localtime, strftime
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

login_manager = LoginManager(app = app)
login_manager.init_app(app)

db = SQLAlchemy(app)
socketio = SocketIO(app)

ROOMLIST = ['Grievances and Feedback', 'Gossip', 'Gaming', 'Music']

@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

@app.route('/', methods = ['GET', 'POST'])
def index():
    regform = RegForm()
    if regform.validate_on_submit():
        name = regform.name.data
        email = regform.email.data
        username = regform.username.data
        password = regform.password.data

        hashed = pbkdf2_sha512.hash(password)
        
        user = UserModel(name = name, email = email, username = username, password = hashed)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('index.html', form = regform)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = UserModel.query.filter_by(username = loginform.username.data).first()
        login_user(user)
        
        return redirect(url_for('chatrooms'))
    return render_template('login.html', form = loginform)

@app.route('/chatrooms', methods = ['GET', 'POST'])
def chatrooms():
    return render_template('chatrooms.html', username = current_user.username, rooms = ROOMLIST)

@app.route('/logout', methods = ['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@socketio.on('message')
def message(data):
    print(f"\n{data}\n")
    send({
        'msg' : data['msg'],
        'username' : data['username'],
        'timestamp' : strftime('%b-%d %I:%M%p', localtime())
    }, room = data['room'])

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({
        'msg' : data['username'] + " joined " + data['room']
    }, room = data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({
        'msg' : data['username'] + " left " + data['room']
    }, room = data['room'])

if __name__ == "__main__":
    app.run()