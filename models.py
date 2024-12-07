from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(255), nullable=True)

    infos = db.relationship('Info', backref='user', cascade="all, delete-orphan")
    sessions = db.relationship('Session', backref = 'user', cascade = 'all, delete-orphan')

class Info(db.Model):
    __tablename__ = 'info'

    info_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    age = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    transport = db.Column(db.String(50), nullable=True)
    budget = db.Column(db.BigInteger, nullable=True)
    purpose = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=True)
    num = db.Column(db.String(50), nullable=True)
    decide_place = db.Column(db.Boolean, nullable=True)
    place = db.Column(db.String(50), nullable=False)
    decide_date = db.Column(db.Boolean, nullable=True)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    decide_span = db.Column(db.Boolean, nullable=True)
    span_approx = db.Column(db.String(50), nullable=False)
    span_month = db.Column(db.Integer, nullable=False)
    span_week = db.Column(db.Integer, nullable=False)
    span_day = db.Column(db.Integer, nullable=False)

    infodetail = db.relationship('InfoDetail', backref='info', uselist=False, cascade="all, delete-orphan")
    sessionss = db.relationship('Session', backref = 'info', cascade = 'all, delete-orphan')

class InfoDetail(db.Model):
    __tablename__ = 'infodetail'
    info_id = db.Column(db.Integer, db.ForeignKey('info.info_id'), primary_key=True)
    detail_purpose = db.Column(db.String(100))
    interest = db.Column(db.String(100))
    special_place = db.Column(db.String(100))
    religion = db.Column(db.String(100))
    consideration = db.Column(db.String(500))

class Session(db.Model):
    __tablename__ = 'session'
    session_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    info_id = db.Column(db.Integer, db.ForeignKey('info.info_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_start = db.Column(db.DateTime, nullable = True)
    session_end = db.Column(db.DateTime, nullable = True)
    session_title = db.Column(db.String(100), nullable = True)

    message = db.relationship('Message', backref = 'session', cascade = 'all, delete-orphan')

class Sender(Enum):
    question = 'question'
    answer = 'answer'

class Message(db.Model):
    __tablename__ = 'message'
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.session_id', ondelete='CASCADE'))
    parent_id = db.Column(db.Integer, db.ForeignKey('message.message_id', ondelete='SET NULL'), nullable=True)
    sender = db.Column(db.Enum(Sender), nullable=True)
    content = db.Column(db.String(5000))
    timestamp = db.Column(db.DateTime)

    # 명시적으로 primaryjoin 조건 설정
    replies = db.relationship(
        'Message',
        backref=db.backref('parent', remote_side=[message_id]),
        primaryjoin="Message.parent_id == Message.message_id",
        lazy='dynamic',
        cascade="all, delete-orphan"
    )
