from flask import render_template, url_for, flash, redirect, request
from chatApp import app, db, bcrypt, socketio
from chatApp.forms import RegistrationForm, LoginForm
from chatApp.models import User, Room
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import json
from time import localtime, strftime

ROOMS = ['potterheads', 'f1', 'mcu stans', 'anything football', 'cs', 'memegrounds']

@app.route("/")
@app.route("/home")
def home():
	if current_user.is_authenticated:
		userList = User.query.all()
		return render_template('chat.html', roomList = ROOMS, room = 'global chat', userList = userList)
	return render_template('chat.html', roomList = ROOMS, room = 'global chat')

@app.route("/chat")
def chat():
	if current_user.is_authenticated:
		userList = User.query.all()
		return render_template('chat.html', roomList = ROOMS, room = 'global chat', userList = userList)
	return render_template('chat.html', roomList = ROOMS, room = 'global chat')


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
	msgToDeliver = {'sender':msgDict['sender'], 'receiver':msgDict['receiver'], 'content':msgDict['content'], 'timestamp':strftime("%I:%M %p", localtime()), 'room':msgDict['room']}
	print("\n\n{}\n\n".format(msgDict))
	if(msgDict['room'] == 'GLOBAL'):
		send(json.dumps(msgToDeliver), broadcast=True)
	elif msgDict['room'].lower() in ROOMS:
		send(json.dumps(msgToDeliver), room = msgToDeliver['room'])
	elif msgDict['room'].lower() not in ROOMS:	# One-to-one
		# roomname1 = msgDict['receiver'] + '_' + msgDict['sender']
		row1 = Room.query.filter_by(roomname=msgDict['room']).first()
		# row2 = Rooms.query.filter_by(roomname=roomname1).first()
		print("Message from {} to {}".format(msgDict['sender'], msgDict['receiver']));
		if row1:
			row = row1
		# if row2:
			# row = row2
		else:
			print("/nerror in handle message/n")
			return 
		row.count = row.count + 1
		print("row.count:", row.count)
		print("row.message", row.message)
		dict1 = json.loads(row.message)
		
		dict1[row.count] = msgDict
		row.message = json.dumps(dict1)
		db.session.commit()
		send(json.dumps(msgToDeliver), room = msgToDeliver['room'])


@socketio.on('join')
def join(data):
	data = json.loads(data);
	print('\n\n', data)
	join_room(data['room'])
	msgToDeliver = {
		'sender':'SYSTEM',
		'content':"{} has joined {}".format(data['sender'], data['room']),
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
		'content':"{} has left {}".format(data['sender'], data['room']),
		'timestamp':strftime('%I:%M %p', localtime())
	}
	send(json.dumps(msgToDeliver), room = data['room'])

@socketio.on('connect')
def connect():
	user = User.query.filter_by(username = current_user.username).first()
	user.last_sid = request.sid
	db.session.commit()
	# user.updateSessionID(request.sid)
	print('\n\n', user)

	

@socketio.on('request_for_connection')
def request_for_connection(request):
	request = json.loads(request)
	print('\n\n', request)
	# Search for recepient of request, named as recipient
	recipient = User.query.filter_by(username = request['to']).first()
	print("\n\nIn request_for_connection:\n{}\n\n".format(recipient))
	emit('request_to_connect', json.dumps(request), room = recipient.last_sid)

@socketio.on('accept_request')
def accept_request(accept_msg):
	accept_msg = json.loads(accept_msg)
	print('\n\n', accept_msg)
	# Search for sender's entry and use his sid to deliver the request acceptance
	sender = User.query.filter_by(username = accept_msg['sender']).first()
	emit('request_accepted', json.dumps(accept_msg), room = sender.last_sid)


@socketio.on('make_new_room')
def make_new_room(room_name):
	room_name = json.loads(room_name)
	# room_name1 = room_name['receiver'] + '_' + room_name['sender']
	# row1 = Rooms.query.filter_by(roomname=room_name1).first()
	row2 = Room.query.filter_by(roomname=room_name['room']).first()
	if not row2:
		row = Room(roomname=room_name['room'])
		db.session.add(row)
		db.session.commit()
	# elif row1:
		# emit('load_history', row1.message, room=row1.roomname)
	elif row2:
		emit('load_history', row2.message, room=row2.roomname)
	else:
		print("/nNot a new room/n")
