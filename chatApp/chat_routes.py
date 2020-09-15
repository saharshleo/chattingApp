from flask import render_template, url_for, flash, redirect, request
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_login import login_required
import json
from time import localtime, strftime

from chatApp import app, db, socketio
from chatApp.models import User, Room
from chatApp.forms import LoginForm
from flask_login import current_user


def make_room_name(room, current_user):
	'''
	Forms the room name depending on the users in the room, and does not include username of current_user
	'''
	users = list(filter(lambda u: u.id != current_user.id, room.users))
	if len(users) == 0:
		raise TypeError('Invalid room, the only member is current user')
	elif len(users) == 1:
		return users[0].username
	elif len(users) == 2:
		return f'{users[0].username} and {users[1].username}'
	else:
		return f'{users[0].username}, {users[1].username} + {len(users)-2}'


@app.route("/chat")
@login_required
def chat():
	if current_user.is_authenticated:
		rooms = current_user.rooms
		chat_list = list(map(lambda room: {
			"chat_name": room.room_name if room.room_name else make_room_name(room, current_user),
			"id": room.id
		}, rooms))
		return render_template("chat.html", chat_list=chat_list)
	return redirect('/login')


@app.route("/chat/new", methods=["GET", "POST"])
@login_required
def new_chat():
	'''
	Handler for POST request to create a new chat room
	Expects an application/json request:
	{
		usernames: <list of usernames>,
		roomName: (not required)
	}
	'''
	if request.method == "POST":
		usernames = request.json.users
		room_name = request.json.roomName
		# Add checks here, e.g. min 2 users, current_user is part of user_list
		# Put below lines in try-except, for e.g. if a user does not exist
		users = set()
		for username in usernames:
			user = User.query.filter_by(username=username).first()
			if user:
				users.add(user)
			else:
				# throw err, user does not exist
				pass
		room = Room(room_name=room_name, users=list(users))
		db.session.add(room)
		db.session.commit()
		return 201
	else:
		return render_template('new_chat.html')

