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

    def __repr__(self):
        return "('{}', '{}')".format(self.username, self.email)


class Rooms(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	roomname = db.Column(db.String(250), unique=True, nullable=False)
	message = db.Column(db.String(250), nullable=False)
	sender = db.Column(db.String(20), nullable=False)
	time_stamp = db.Column(db.String(100), nullable=False)