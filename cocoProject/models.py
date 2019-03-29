from cocoProject import db, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)
    dev_id = db.Column(db.String(256), nullable=False, unique=True)
    coco = db.relationship('Coco', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

class Coco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    img = db.Column(db.String(256), nullable=True)
    proxy = db.Column(db.String(256), nullable=True, unique=True)
    address = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)