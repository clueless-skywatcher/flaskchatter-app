#Import all the necessary libraries
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from wtforms_forms import *
from models import UserModel
from passlib.hash import pbkdf2_sha512
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from time import localtime, strftime
import os

#Initialize the app; Deploying the app on Heroku takes care of the database URL for us
app = Flask(__name__)
app.secret_key = 'notthedeployedsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5432/messagedb'

# app.secret_key = os.environ.get('SECRET')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

#Initialize the login manager to look after the logged in user sessions
login_manager = LoginManager(app = app)
login_manager.init_app(app)

#Initialize the database via SQLAlchemy
db = SQLAlchemy(app)

#Initialize the SocketIO; It uses the concept of websockets, integral in developing the main chat activities
socketio = SocketIO(app)

#Initialize what rooms to show to the users
ROOMLIST = ['Grievances and Feedback', 'Gossip', 'Gaming', 'Music']

#Get the id of the user who logged in just now
@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

# Route to the index page
# Present a registration form to the user that requires a name, email, username and password
# The password is sent to the database alongwith the other details in a 
# hashed format using the PBKDF2 algorithm.
# After completion of registration the user is logged in to the login page.
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

# Login route
# If the user details provided in the login form are successfully validated
# check whether the given username exists in the system, if exists, then redirect
# to the chatroom page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():
        user = UserModel.query.filter_by(username = loginform.username.data).first()
        login_user(user)
        return redirect(url_for('chatrooms'))
    return render_template('login.html', form = loginform)

# The chatroom route, renders the chatrooms template, passing the roomlist and username as parameters
@app.route('/chatrooms', methods = ['GET', 'POST'])
def chatrooms():
    return render_template('chatrooms.html', username = current_user.username, rooms = ROOMLIST)

# Logout route
# Redirects to the login page after logging out
@app.route('/logout', methods = ['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

# While the websocket is on, if an incoming message event is triggered
# send the message to the client
@socketio.on('message')
def message(data):
    print(f"\n{data}\n")
    send({
        'msg' : data['msg'],
        'username' : data['username'],
        'timestamp' : strftime('%b-%d %I:%M%p', localtime())
    }, room = data['room'])

# If a new user joins the current room, trigger an event to notify the client
# about the new user's arrival
@socketio.on('join')
def join(data):
    join_room(data['room'])    
    send({
        'msg' : data['username'] + " joined " + data['room']
    }, room = data['room'])

# If a current user leaves the room, trigger an event to notify the client
# about the user's departure.
@socketio.on('leave')
def leave(data):
    ONLINE_USERS.remove(data['username'])
    leave_room(data['room'])
    send({
        'msg' : data['username'] + " left " + data['room']
    }, room = data['room'])

if __name__ == "__main__":
    socketio.run(app, debug = True)