from flask import Blueprint, jsonify, request
from models import db, Info, InfoDetail
from models import db, Session

session = Session.query.filter_by(user_id = 7)
print(session.session_title)