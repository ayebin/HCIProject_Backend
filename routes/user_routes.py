from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, db 

user_bp = Blueprint('user_bp', __name__)

# Route: Signup
@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('user_id')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "아이디와 비밀번호를 입력해주세요."}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        # Check if user exists
        existing_user = Users.query.filter_by(user_id=username).first()
        if existing_user:
            return jsonify({"error": "이미 존재하는 아이디입니다."}), 400

        # Create new user
        new_user = Users(user_id=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "회원가입 성공"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

# Route: Login
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('user_id')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "아이디와 비밀번호를 입력해주세요."}), 400

    try:
        # Find user in DB
        user = Users.query.filter_by(user_id=username).first()
        if not user:
            return jsonify({"error": "아이디가 존재하지 않습니다."}), 404

        if not check_password_hash(user.password, password):
            return jsonify({"error": "비밀번호가 틀렸습니다."}), 401

        return jsonify({"message": "로그인 성공", "redirect": "/home", "id": user.id, "name": user.user_id}), 200
    except Exception as e:
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

# Route: Delete Account
@user_bp.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    username = data.get('user_id')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "아이디와 비밀번호를 입력해주세요."}), 400

    try:
        # Find user in DB
        user = Users.query.filter_by(user_id=username).first()
        if not user:
            return jsonify({"error": "아이디가 존재하지 않습니다."}), 404

        if not check_password_hash(user.password, password):
            return jsonify({"error": "비밀번호가 틀렸습니다."}), 401

        # Delete user
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "계정 삭제 성공", "redirect": "/home"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500
