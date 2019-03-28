from cocoProject import app, db
from flask import render_template, request, redirect, flash, url_for, Markup
from flask_login import current_user, login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from werkzeug.urls import url_parse
import datetime
from flask_babel import _
from cocoProject.forms import LoginForm, RegisterForm
from cocoProject.models import User


@app.route('/index')
def index():

    return render_template("index.html")

@app.route('/')
@app.route('/signin',methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        username = username.lower()
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('Username or Password Incorrect'))
            return redirect(url_for('signin'))
        if sha256_crypt.verify(password,user.pw_hash):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            flash(_('Welcome %(username)s', username=user.username))
            return redirect(next_page)
        else:
            flash(_('Username or Password Incorrect'))
            return redirect(url_for('signin'))
    return render_template("signin.html", form=form)

@app.route('/register',methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username=username,pw_hash=sha256_crypt.encrypt(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(_('Registration Successful!.'))
        return redirect(url_for('index'))
    return render_template("register.html",form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))