from datetime import datetime
from chatApp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


room_user = db.Table('room_user',
	db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	messages = db.relationship('Message', backref='user', lazy=True)
	rooms = db.relationship('Room', secondary=room_user)

	def __repr__(self):
		return "User<ID:{}, Email:{}, Username:{}>".format(self.id, self.email, self.username)


class Room(db.Model):
	# __bind__ = 'rooms'
	id = db.Column(db.Integer, primary_key=True)
	room_name = db.Column(db.String(255), default="Chat")
	messages = db.relationship('Message', backref='room', lazy=True)
	users = db.relationship('User', secondary=room_user)

	def __repr__(self):
		return "Room<ID:{}, Room name:{}>".format(self.id, self.room_name)


class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False)
	room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  # Or should I keep null for global chat room?
	sender = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

	def __repr__(self):
		return "Message<ID:{}, Content:{}..., Room:{}, Sender:{}>".format(self.id, self.content[:5], self.room, self.sender)

