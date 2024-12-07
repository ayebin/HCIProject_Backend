from flask import Blueprint, jsonify, request
from models import db, Session
from datetime import datetime

session_bp = Blueprint('session_bp', __name__)

@session_bp.route('/session', methods=['POST'])
def add_session():
    data = request.get_json()
    info_id = data.get('info_id')
    user_id = data.get('user_id')
    print(f"User ID: {user_id}, Info ID: {info_id}")
    print(datetime.now())

    try:
        new_session = Session(
            info_id = data.get('info_id'),
            user_id = data.get('user_id'),
            session_start = datetime.now()
        )
        db.session.add(new_session)
        db.session.commit()

        return jsonify({
            "message": "Session created successfully!",
            'session_id': new_session.session_id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
