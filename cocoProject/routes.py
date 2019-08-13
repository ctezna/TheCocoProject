from cocoProject import app, db
from flask import render_template, request, redirect, flash, url_for, Markup
from flask_login import current_user, login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from werkzeug.urls import url_parse
import datetime, os, requests, json, secrets
from flask_babel import _
from cocoProject.forms import LoginForm, RegisterForm, AddCocoForm, AddRoutineForm, EditCocoForm, EditProfileForm
from cocoProject.models import User, Coco, Routine
from cocoProject import remoteit_api, addRoutine
from PIL import Image


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    cocos = Coco.query.filter_by(user_id=user.id).all()
    form = AddRoutineForm()
    if form.validate_on_submit():
        task = form.task.data
        days = [form.mon.data, form.tue.data, form.wed.data, form.thur.data, form.fri.data, form.sat.data, form.sun.data]
        week = ['Monday, ', 'Tuesday, ', 'Wednesday, ', 'Thursday, ', 'Friday, ', 'Saturday, ', 'Sunday']
        action_days = ''
        for i in range(len(days)):
            if days[i] == True:
                action_days += week[i]
        times = form.times.data
        proxy = form.proxy.data
        coco = Coco.query.filter_by(proxy=proxy).first_or_404()
        routine = Routine(task=task, days=action_days, times=times, coco_id=coco.id)
        db.session.add(routine)
        db.session.commit()
        routine = addRoutine.send(proxy, task, action_days, times)
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

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    id = request.form['id']
    coco = Coco.query.filter_by(id=id).first_or_404()
    routines = Routine.query.filter_by(coco_id=id).all()
    msg = Markup('<strong>{}</strong> Erased.'.format(coco.name))
    for r in routines:
        db.session.delete(r)
        db.session.commit()
    db.session.delete(coco)
    db.session.commit()
    flash(_(msg),'warning')
    return redirect(url_for('index'))

@app.route('/deleteRoutine', methods=['POST'])
@login_required
def deleteRoutine():
    id = request.form['id']
    routine = Routine.query.filter_by(id=id).first_or_404()
    msg = Markup('<strong>{}</strong> Routine Erased.'.format(routine.task))
    db.session.delete(routine)
    db.session.commit()
    flash(_(msg),'warning')
    return redirect(url_for('index'))

@app.route('/refresh/<id>', methods=['GET','POST'])
@login_required
def refresh(id):
    form = AddCocoForm()
    coco = Coco.query.filter_by(id=id).first_or_404()
    routines = Routine.query.filter_by(coco_id=id).all()
    response = requests.get(coco.proxy+'/reboot')
    msg = Markup('Coco Restarting. Please wait for <strong>light to turn on.</strong>')
    flash(_(msg), 'info')
    for r in routines:
        db.session.delete(r)
        db.session.commit()
    db.session.delete(coco)
    db.session.commit()
    return redirect(url_for('connectCoco'))

# @app.route('/proxyGen/<id>', methods=['GET', 'POST'])
# @login_required
# def proxyGen(id):


def save_img(img_data):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(img_data.filename)
    img_filename = random_hex + f_ext
    img_path = os.path.join(app.root_path, 'static/img/cocoPics', img_filename)
    output_size = (150,150)
    img = Image.open(img_data)
    img.thumbnail(output_size)
    img.save(img_path)
    return img_filename

@app.route('/connectCoco', methods=['GET', 'POST'])
@login_required
def connectCoco():
    form = AddCocoForm()
    form.password.data = current_user.password
    if form.validate_on_submit():
        name = form.name.data
        if form.img.data:
            img_name = save_img(form.img.data)
            img = 'cocoPics/' + img_name
        else:
            img = 'Logo_small.png'
        address = form.address.data
        password = form.password.data
        user_id = current_user.id
        token = remoteit_api.login(current_user.dev_id, current_user.username, password)
        proxy = remoteit_api.connect(current_user.dev_id, token, address)
        if token == 800:
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
    routines = Routine.query.filter_by(coco_id=coco.id).all()
    form = EditCocoForm()
    if form.validate_on_submit():
        if form.img.data:
            img_name = save_img(form.img.data)
            img = 'cocoPics/' + img_name
            coco.img = img
        name = form.name.data
        coco.name = name
        db.session.commit()
        flash(_('Coco data changed successfully.'), 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.name.data = coco.name
    return render_template("cocoProfile.html", coco=coco, routines=routines, form=form)

@app.route('/userProfile/<username>', methods=['GET', 'POST'])
@login_required
def userProfile(username):
    form = EditProfileForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        user.pw_hash = sha256_crypt.encrypt(form.password.data)
        user.dev_id = form.devKey.data
        db.session.commit()
        flash(_('Profile changes successful.'), 'success')
        return redirect(url_for('userProfile', username=user.username))
    elif request.method == 'GET':
        form.devKey.data = current_user.dev_id
    return render_template("userProfile.html", user=user, form=form)

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