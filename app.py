from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_bcrypt import Bcrypt

import config
import time
import math
import torch
import numpy as np
import base64
import PIL.ImageOps
from io import BytesIO
from PIL import Image
from forward import forwardModel, cat

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)
socketio = SocketIO(app)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from forms import SigninForm, SignupForm, PostForm, EditForm, ResetForm
from models import User, Post

model = forwardModel()
result_fake = result_real = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('homepage', nickname=current_user.username))
    return render_template('base.html')

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    posts = Post.query.order_by(Post.likes.desc()).all()
    return render_template('explore.html', posts=posts)

@app.route('/playground', methods=['GET', 'POST'])
def playground():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        category = form.category.data
        style = form.style.data
        article = form.article.data
        date_posted = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        ids = form.img.data.split(',')
        imglist = ''
        for i in ids:
            path = './static/imgdata/' + str(int(time.time()*math.pow(10,6))) + '.png'
            img = result_fake[int(i)%10]
            img.save(path,'png')
            imglist += path + ' '
        post = Post(title=title, category=category, style=style, username=current_user.username, imglist=imglist, article=article, date_posted=date_posted)
        user = User.query.filter_by(username=current_user.username).first()
        user.posts.append(post)
        db.session.commit()
        socketio.emit('submit', {"msg": "Submit success"}, namespace='/playground')
    return render_template('playground.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('homepage', nickname=current_user.username))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('signIn.html', title="SignIn", form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect('signin')
    return render_template('signUp.html', title="SignUp", form=form)

@app.route('/resetpasswd', methods=['GET', 'POST'])
def resetpasswd():
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.username==form.username.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            return redirect('signin')
        else:
            flash('Authentication failed: username does not match email','danger')
    return render_template('forget.html', title="ResetPasswd", form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')

@app.route('/homepage/<nickname>', methods=['GET', 'POST'])
def homepage(nickname):
    posts = Post.query.filter_by(username=nickname).order_by(Post.date_posted.desc()).all()
    return render_template('page.html', nickname=nickname, posts=posts)

@app.route('/edit/<postid>', methods=['GET', 'POST'])
def edit(postid):
    form = EditForm()
    post = Post.query.get(postid)
    if form.validate_on_submit():
        post.title = form.title.data
        post.category = form.category.data
        post.article = form.article.data
        db.session.commit()
        return redirect(url_for('homepage', nickname=current_user.username))
    return render_template('edit.html', nickname=current_user.username, post=post, form=form)

@app.route('/delete/<postid>', methods=['GET', 'POST'])
def delete(postid):
    post = Post.query.get(postid)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('homepage', nickname=current_user.username))

@app.route('/like/<postid>', methods=['GET', 'POST'])
def like(postid):
    post = Post.query.get(postid)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('explore'))

@socketio.on('cav', namespace='/playground')
def playground_message(message):
    global result_fake, result_real
    img = base64_to_image(message['data'][22:])
    model.set_edge(np.asarray(img))
    if(message['refresh']):
        model.resample(int(message['id']))
    result_fake, result_real, _, _, _ = model.forward()
    msg = {
        "id": message['id'],
        "data_0": image_to_base64(result_fake[0]),
        "data_1": image_to_base64(result_fake[1]),
        "data_2": image_to_base64(result_fake[2]),
        "data_3": image_to_base64(result_fake[3]),
        "data_4": image_to_base64(result_fake[4]),
        "data_5": image_to_base64(result_fake[5]),
        "data_6": image_to_base64(result_fake[6]),
        "data_7": image_to_base64(result_fake[7]),
        "data_8": image_to_base64(result_fake[8]),
        "data_9": image_to_base64(result_fake[9]),
	    "data_10": image_to_base64(result_fake[10]),
        "data_11": image_to_base64(result_fake[11])
    }
    emit('my response', msg, namespace='/playground')

@socketio.on('connect', namespace='/playground')
def playground_connect():
    print('connect')

@socketio.on('disconnect', namespace='/playground')
def playground_disconnect():
    print('Client disconnected')

def base64_to_image(base64_data, image_path=None):
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    try:
        img_f = Image.open(image_data).convert('RGB')
        img = PIL.ImageOps.invert(img_f)
        if image_path:
            img.save(image_path)
        return img.resize((512,512))
    except(OSError, NameError):
        print('OSError')

def image_to_base64(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

if __name__ == '__main__':
    # app.run(debug=True, use_reloader=True)
    # socketio.run(app, debug=True, use_reloader=True)
    socketio.run(app, debug=False, use_reloader=True)
