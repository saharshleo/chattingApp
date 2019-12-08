from datetime import datetime
from chatApp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	last_sid = db.Column(db.String(120)) # no idea about str length or uniqueness or nullability

	def __repr__(self):
		return "('ID:{}', 'Email:{}', 'Username:{}', 'Last_SID{}')".format(self.id, self.email, self.username, self.last_sid)

	
class Rooms(db.Model):
	__bind__ = 'rooms'
	id = db.Column(db.Integer, primary_key=True)
	roomname = db.Column(db.String(250), unique=True)
	message = db.Column(db.String(50000), default='{"0":""}')
	count = db.Column(db.Integer, default=0)
	
	def __repr__(self):
		return "('ID:{}', 'roomname:{}', 'count:{}')".format(self.id, self.roomname, self.count)
