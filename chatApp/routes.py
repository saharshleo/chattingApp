from flask import render_template, url_for, flash, redirect, request
from chatApp import app, db, bcrypt, socketio
from chatApp.forms import RegistrationForm, LoginForm
from chatApp.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, send, join_room, leave_room
import json
from time import localtime, strftime

ROOMS = ['potterheads', 'f1', 'MCU stans', 'anything football', 'CS', 'memeGrounds']

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', roomList = ROOMS, room = 'global chat')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if  form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

# @app.route("/chatroom/<string:roomName>")
# def chatroom(roomName):
#     return render_template('room.html', room = roomName, roomList = ROOMS)


''' SOCKET.IO EVENTS '''

@socketio.on('message')
def handleMessage(msg):
    msgDict = json.loads(msg)
    msgToDeliver = {'sender':msgDict['sender'], 'content':msgDict['content'], 'timestamp':strftime("%I:%M %p", localtime()), 'room':msgDict['room']}
    print(f"\n\n{msgDict}\n\n")
    if(msgDict['room'] == 'GLOBAL'):
        send(json.dumps(msgToDeliver), broadcast=True)
    else:
        send(json.dumps(msgToDeliver), room = msgToDeliver['room'])
    
@socketio.on('join')
def join(data):
    data = json.loads(data);
    print('\n\n', data)
    join_room(data['room'])
    msgToDeliver = {
        'sender':'SYSTEM',
        'content':f"{data['sender']} has joined {data['room']}",
        'timestamp':strftime('%I:%M %p', localtime())
    }
    send(json.dumps(msgToDeliver), room = data['room'])

@socketio.on('leave')
def leave(data):
    data = json.loads(data);
    print('\n\n', data)
    leave_room(data['room'])
    msgToDeliver = {
        'sender':'SYSTEM',
        'content':f"{data['sender']} has left {data['room']}",
        'timestamp':strftime('%I:%M %p', localtime())
    }
    send(json.dumps(msgToDeliver), room = data['room'])
