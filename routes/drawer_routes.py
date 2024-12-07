from flask import Blueprint, jsonify, request
from models import db, Session
import re

drawer_bp = Blueprint('drawer_bp', __name__)

@drawer_bp.route('/list', methods=['GET'])
def get_session():
    user_id = int(request.args.get('user_id'))
    print(f'drawer: {user_id}')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        sessions = Session.query.filter_by(user_id=user_id).order_by(Session.session_end.desc()).all()
        print(sessions)

        sesh_num = []
        for sesh in sessions:
            sesh = str(sesh)
            num = re.search(r'\d+', sesh)
            if num:
                sesh_num.append(int(num.group()))
        
        print(f'sesh_num : {sesh_num}')

        session_list = []
        for num in sesh_num:
            sesh = Session.query.filter_by(session_id=num).first()
            temp_dict = {}
            temp_dict['session_id'] = num
            temp_dict['info_id'] = sesh.info_id
            if sesh.session_title is None:
                temp_dict['session_title'] = '대화가 없습니다.'
                temp_dict['session_end'] = '2024-12-01 00:00:00'
            else:
                temp_dict['session_title'] = sesh.session_title
                temp_dict['session_end'] = sesh.session_end.isoformat()
            session_list.append(temp_dict)
        print(session_list)

        return jsonify(session_list), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

