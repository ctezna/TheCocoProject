from cocoProject import app, db
from flask import render_template, request, redirect, flash, url_for, Markup
from flask_login import current_user, login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from werkzeug.urls import url_parse
import datetime, os, requests, json
from flask_babel import _
from cocoProject.forms import LoginForm, RegisterForm, AddCocoForm, AddRoutineForm
from cocoProject.models import User, Coco
from cocoProject import remoteit_api, addRoutine


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    cocos = Coco.query.filter_by(user_id=user.id).all()
    form = AddRoutineForm()
    if form.validate_on_submit():
        task = form.task.data
        days = [form.mon.data, form.tue.data, form.wed.data, form.thur.data, form.fri.data, form.sat.data, form.sun.data]
        times = form.times.data
        proxy = form.proxy.data
        routine = addRoutine.send(proxy, task, days, times)
        flash(_('Routine Added Successfully.'),'success')
    elif request.method == 'POST':
        proxy = request.form['data']
        id = request.form['id']
        coco = Coco.query.filter_by(id=id).first_or_404()
        if proxy.split('/')[3] == 'feed':
            msg = Markup('Feeding <strong>{}</strong>. . .'.format(coco.name))
            cat = 'info'
        elif proxy.split('/')[3] == 'lightOn':
            msg = Markup('Light Activated for <strong>{}</strong>.'.format(coco.name))
            cat = 'warning'
            coco.light = 1
            db.session.commit()
        elif proxy.split('/')[3] == 'lightOff':
            msg = Markup('Light Deactivated for <strong>{}</strong>.'.format(coco.name))
            cat = 'secondary'
            coco.light = 0
            db.session.commit()
        response = requests.get(proxy)
        flash(_(msg),cat)
    return render_template("index.html", cocos=cocos, form=form)

@app.route('/connectCoco', methods=['GET', 'POST'])
@login_required
def connectCoco():
    form = AddCocoForm()
    if form.validate_on_submit():
        name = form.name.data
        img = form.img.data
        address = form.address.data
        password = form.password.data
        user_id = current_user.id
        proxy = remoteit_api.connect(current_user.dev_id, current_user.username, password, address)
        if proxy == 800:
            flash(_('Error Establishing Connection. Please check credentials and try again.'),'danger')
            return redirect(url_for('connectCoco'))
        elif proxy == 801:
            flash(_('Timeout Error. Please try again.'),'danger')
            return redirect(url_for('connectCoco'))
        coco = Coco(name=name, img=img, proxy=proxy, address=address, user_id=user_id)
        db.session.add(coco)
        db.session.commit()
        flash(_('New Coco Added Successfully!'),'success')
        return redirect(url_for('index'))
    return render_template("connectCoco.html", form=form)

@app.route('/cocoProfile/<id>', methods=['GET', 'POST'])
@login_required
def cocoProfile(id):
    coco = Coco.query.filter_by(id=id).first_or_404()
    return render_template("cocoProfile.html", coco=coco)

@app.route('/userProfile', methods=['GET', 'POST'])
@login_required
def userProfile():
    return render_template("userProfile.html")

@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
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
            flash(_('Welcome %(username)s', username=user.username),'primary')
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
        devKey = form.devKey.data
        user = User(username=username,pw_hash=sha256_crypt.encrypt(password), dev_id=devKey)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(_('Registration Successful!'),'primary')
        return redirect(url_for('index'))
    return render_template("register.html",form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))