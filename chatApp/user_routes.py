from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from chatApp import app, db, bcrypt
from chatApp.models import User
from chatApp.forms import RegistrationForm, LoginForm

@app.route("/user/register", methods=['GET', 'POST'])
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


@app.route("/user/login", methods=['GET', 'POST'])
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


@app.route("/user/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/user/account")
@login_required
def account():
	return render_template('account.html', title='Account')


@app.route("/user", methods=["POST"])
@login_required
def find_user():
	'''
	Handler for POST request to search for users by usernames (prefix)
	Expects an application/json request:
	{
		searchValue: <prefix>
	}
	Returns JSON:
	{
		usernames: <list of usernames>
	}
	'''
	users = User.query.filter(User.username.beginswith(request.searchValue))
	users = list(filter(lambda user: user.id != current_user.id, users))
	usernames = list(map(lambda user: user.username, users))
	return {
		'usernames': usernames
	}