from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy.exc import InvalidRequestError

class Schools(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64))
    country = db.Column(db.String(64))
    username = db.Column(db.String(16), unique=True, index=True)
    password = db.Column(db.String(16))
    description = db.Column(db.String(512))
    header_img = db.Column(db.String(64))
    works = db.relationship('Work', backref='user')

    def check_password(self, password):
        return check_password_hash(generate_password_hash(self.password), password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(user_id):
    user = None
    try:
        user = Schools.query.get(int(user_id))
    except InvalidRequestError:
        db.session.rollback()
        user = Schools.query.get(int(user_id))
    return user


class Media(db.Model):
    __tablename__ = 'uploaded-media'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    upload_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    path = db.Column(db.String(64))
    type = db.Column(db.Integer)

    def __repr__(self):
        return "<id={}, author_id={}, upload_date={}, type={}>, path={}>".format(self.id, self.author_id, self.upload_date, self.type, self.path)


class Work(db.Model):
    __tablename__ = 'uploaded-projects'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    upload_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    title = db.Column(db.String(64))
    attached_media = db.Column(db.String(64))
    description = db.Column(db.Text)

    def __repr__(self):
        return '<Post {}>'.format(self.body)
