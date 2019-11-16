from cocoProject import app, db
from flask import render_template, request, redirect, flash, url_for, Markup, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from passlib.hash import sha256_crypt
from werkzeug.urls import url_parse
import os, requests, json, secrets
from datetime import datetime
from flask_babel import _
from cocoProject.forms import LoginForm, RegisterForm, AddCocoForm, AddRoutineForm, EditCocoForm, EditProfileForm
from cocoProject.models import User, Coco, Routine
from cocoProject import remoteit_api, routine_control
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
        light_splice = ''
        if task == 'Light':
            color = request.form['color'].lstrip('#')
            clen = len(color)
            rgb = tuple(int(color[i:i+clen//3], 16) for i in range(0, clen, clen//3))
            light_splice = '{},{},{},{}'.format(rgb[0], rgb[1], rgb[2], request.form['brightInput'])

        
        if coco.deviceType == 'horus':
            if task == 'Dispense Food':
                flash(_('Routine Unavailable for Device Model'), 'danger')
                return render_template("index.html", cocos=cocos, form=form)
            proxy = 'https://ctezna.ngrok.io/routine'

        response = routine_control.send(routine.id, proxy, task, action_days, times, light_splice)
        if response == 0:
            db.session.remove(routine)
            db.session.commit()
            flash(_('Routine Created Unsuccessfully.'),'danger')
            return render_template("index.html", cocos=cocos, form=form)
        flash(_('Routine Added Successfully.'),'success')
    
    for c in cocos:
        try:
            proxy = ''
            if c.deviceType == 'coco':
                proxy = c.proxy
            elif c.deviceType == 'horus':
                proxy = 'https://ctezna.ngrok.io'
            rsp = requests.get(proxy + '/light/status').json()
        except json.decoder.JSONDecodeError:
            address = c.address
            password = c.cred
            token = remoteit_api.login(current_user.dev_id, current_user.username, password)
            proxy = remoteit_api.connect(current_user.dev_id, token, address)
            if not type(proxy) == int:
                c.proxy = proxy
                proxy = ''
                if c.deviceType == 'coco':
                    proxy = c.proxy
                elif c.deviceType == 'horus':
                    proxy = 'https://ctezna.ngrok.io'

                try: 
                    rsp = requests.get(proxy + '/light/status').json()
                except json.decoder.JSONDecodeError:
                    rsp = {
                        'status': False,
                        'red': 255,
                        'green': 255,
                        'blue': 255,
                        'brightness': 0.3
                    }

            else:
                rsp = {
                    'status': False,
                    'red': 255,
                    'green': 255,
                    'blue': 255,
                    'brightness': 0.3
                }
        c.light = rsp['status']
        c.lightColor = '#%02x%02x%02x' % (int(rsp['red']), int(rsp['green']), int(rsp['blue']))
        c.lightBrightness = float(rsp['brightness'])
        print(rsp['status'])
    
    db.session.commit()
    return render_template("index.html", cocos=cocos, form=form)

@app.route('/task', methods=['POST'])
@login_required
def task():
    proxy = request.form['data']
    id = request.form['id']
    coco = Coco.query.filter_by(id=id).first_or_404()
    msg = ''
    cat = ''
    response = requests.get(proxy)
    red = 400
    green = 400
    blue = 400
    brightness = 400
    try:
        red = int(proxy.split('/')[3].split('?')[1].split('&')[0].split('=')[1])
        green = int(proxy.split('/')[3].split('?')[1].split('&')[1].split('=')[1])
        blue = int(proxy.split('/')[3].split('?')[1].split('&')[2].split('=')[1])
        brightness = float(proxy.split('/')[3].split('?')[1].split('&')[3].split('=')[1])
        pass
    except IndexError:
        try:
            red = int(proxy.split('/')[4].split('?')[1].split('&')[0].split('=')[1])
            green = int(proxy.split('/')[4].split('?')[1].split('&')[1].split('=')[1])
            blue = int(proxy.split('/')[4].split('?')[1].split('&')[2].split('=')[1])
            brightness = float(proxy.split('/')[4].split('?')[1].split('&')[3].split('=')[1])
            pass
        except IndexError:
            pass      
        pass

    try:
        taskSuccess = response.json()['response']
        pass
    except:
        taskSuccess = 0
        if response.status_code == 204:
            taskSuccess = 1 
        pass

    if taskSuccess != 1:
        msg = Markup('Task {} Unsuccessful: Please refresh page or \
            use refresh link to generate new proxy.'.format(proxy))
        cat = 'danger'
    elif proxy.split('/')[3] == 'feed' and taskSuccess == 1:
        msg = Markup('Feeding <strong>{}</strong>. . .'.format(coco.name))
        cat = 'info'
    elif proxy.split('/')[3] == 'reboot' and taskSuccess == 1:
        msg = Markup('Coco Restarting. Please wait for <strong>light to turn on.</strong>')
        cat = 'info'
    elif proxy.split('/')[3] == 'camOff':
        taskSuccess = 1 
    elif (red > 0 and red < 300) or \
            (green > 0 and green < 300) or \
            (blue > 0 and  blue < 300) and taskSuccess == 1:
        coco.light = 1
        coco.lightBrightness = brightness
        coco.lightColor = '#%02x%02x%02x' % (red, green, blue)
        db.session.commit()
    elif (red < 0) or \
            (green < 0) or \
            (blue < 0) and taskSuccess == 1:
        msg = Markup('Party for <strong>{}</strong>!'.format(coco.name))
        cat = 'warning'
        coco.light = 1
        coco.lightBrightness = brightness
        db.session.commit()
    elif ((red == 0) and \
            (green == 0) and \
            (blue == 0) and taskSuccess == 1) or (proxy == 'https://ctezna.ngrok.io/light/off'):
        msg = Markup('Light Deactivated for <strong>{}</strong>.'.format(coco.name))
        cat = 'secondary'
        coco.light = 0
        db.session.commit()
    rsp = { 
            "cocoId":coco.id,
            "cocoProxy":coco.proxy,
            "cocoLight":coco.light,
            "lightColor":coco.lightColor,
            "lightBrightness":coco.lightBrightness,
            "msg":msg,
            "msgcat":cat
            }
    return jsonify(rsp)

@app.route('/deleteCoco/<id>', methods=['GET'])
@login_required
def deleteCoco(id):
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

@app.route('/deleteRoutine/<id>', methods=['GET'])
@login_required
def deleteRoutine(id):
    routine = Routine.query.filter_by(id=id).first_or_404()
    coco = Coco.query.filter_by(id=routine.coco_id).first_or_404()
    proxy = ''
    if coco.deviceType == 'coco':
        proxy = coco.proxy
    elif coco.deviceType == 'horus':
        proxy = 'https://ctezna.ngrok.io/routine'
    
    response = routine_control.remove(routine.id, proxy)
    if response == 0:
        msg = Markup('Unable to remove Routine. Please check connection.')
        flash(_(msg),'danger')
        return redirect(url_for('index'))
    msg = Markup('<strong>{}</strong> Routine Erased.'.format(routine.task))
    db.session.delete(routine)
    db.session.commit()
    flash(_(msg),'warning')
    return redirect(url_for('cocoProfile', id=coco.id))

@app.route('/proxyGen/<ids>', methods=['GET'])
@login_required
def proxyGen(ids):
    ids = ids.split(",")
    rsp = []
    for id in ids:
        if id.isdigit():
            coco = Coco.query.filter_by(id=id).first_or_404()
            address = coco.address
            password = coco.cred
            token = remoteit_api.login(current_user.dev_id, current_user.username, password)
            proxy = remoteit_api.connect(current_user.dev_id, token, address)
            if token == 800:
                print("token fail")
            elif proxy == 801:
                print("proxy fail")
            else:
                coco.proxy = proxy
                coco.timeConnection = datetime.utcnow()
                db.session.commit()
            item = { 
                "cocoId":coco.id,
                "cocoProxy":coco.proxy,
                }
            rsp.append(item)
        #print(rsp)
    return jsonify(rsp)


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
        deviceType = form.deviceType.data
        token = remoteit_api.login(current_user.dev_id, current_user.username, password)
        proxy = remoteit_api.connect(current_user.dev_id, token, address)
        if token == 800:
            flash(_('Error Establishing Connection. Please check credentials and try again.'),'danger')
            return redirect(url_for('connectCoco'))
        elif proxy == 801:
            flash(_('Timeout Error. Please try again.'),'danger')
            return redirect(url_for('connectCoco'))
        coco = Coco(name=name, img=img, proxy=proxy, address=address, user_id=user_id, 
                    cred=password, timeConnection=datetime.utcnow(), deviceType=deviceType)
        db.session.add(coco)
        db.session.commit()
        flash(_('New Coco Added Successfully!'),'success')
        return redirect(url_for('index'))
    return render_template("connectCoco.html", form=form)

@app.route('/cocoProfile/<id>', methods=['GET', 'POST'])
@login_required
def cocoProfile(id):
    coco = Coco.query.filter_by(id=id).first_or_404()
    proxy = ''
    if coco.deviceType == 'coco':
        proxy = coco.proxy
    elif coco.deviceType == 'horus':
        proxy = 'https://ctezna.ngrok.io/routine'
    routines = routine_control.get(proxy)
    if routines == 0:
        flash(_('Profile loaded unsucessfully. Check connection.'),'danger')
        return redirect(url_for('index'))
    form = EditCocoForm()
    if form.validate_on_submit():
        if form.img.data:
            img_name = save_img(form.img.data)
            img = 'cocoPics/' + img_name
            coco.img = img
        name = form.name.data
        address = form.address.data
        coco.name = name
        coco.address = address
        db.session.commit()
        flash(_('Coco data changed successfully.'), 'success')
    elif request.method == 'GET':
        form.name.data = coco.name
        form.address.data = coco.address
    return render_template("cocoProfile.html", coco=coco, routines=routines['routines'], form=form)

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