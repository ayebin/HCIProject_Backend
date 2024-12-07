from flask import Blueprint, jsonify, request
from models import db, Info, InfoDetail

info_bp = Blueprint('info_bp', __name__)

# Info 데이터 추가
@info_bp.route('/info', methods=['POST'])
def add_info():
    data = request.get_json()
    try:
        new_info = Info(
            user_id=data['user_id'],
            age=data['age'],
            gender=data['gender'],
            transport=data['transport'],  
            budget=data['budget'],
            purpose=data['purpose'],  
            type=data['type'],  
            num=data['num'],  
            decide_place=data['decide_place'],
            place=data.get('place'),
            decide_date=data['decide_date'],
            date_start=data.get('date_start'),
            date_end=data.get('date_end'),
            decide_span=data['decide_span'],
            span_approx=data.get('span_approx'),
            span_month=data.get('span_month'),
            span_week=data.get('span_week'),
            span_day=data.get('span_day'),
            
        )
        db.session.add(new_info)
        db.session.commit()

        if 'infodetail' in data:
            new_detail = InfoDetail(
                info_id=new_info.info_id,
                detail_purpose=data['infodetail'].get('detail_purpose'),
                interest=data['infodetail'].get('interest'),
                special_place=data['infodetail'].get('special_place'),
                religion=data['infodetail'].get('religion'),
                consideration=data['infodetail'].get('consideration')
            )
            db.session.add(new_detail)
            db.session.commit()

        return jsonify({"message": "Info added successfully!", "info_id": new_info.info_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    


# InfoDetail 데이터 추가
@info_bp.route('/infodetail', methods=['POST'])
def add_infodetail():
    data = request.get_json()
    try:
        info_id = data.get('info_id')
        info = Info.query.get(info_id)

        if not info:
            return jsonify({"error": "Info not found"}), 404

        new_detail = InfoDetail(
            info_id=info_id,
            detail_purpose=data.get('detail_purpose'),
            interest=data.get('interest'),
            special_place=data.get('special_place'),
            religion=data.get('religion'),
            consideration=data.get('consideration')
        )
        db.session.add(new_detail)
        db.session.commit()

        return jsonify({"message": "InfoDetail added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



# Info 데이터 조회
@info_bp.route('/info/<int:info_id>', methods=['GET'])
def get_info(info_id):
    info = Info.query.filter_by(info_id=info_id).first()
    if not info:
        return jsonify({"error": "Info not found"}), 404

    info_detail = InfoDetail.query.filter_by(info_id=info_id).first()
    result = {
        "info_id": info.info_id,
        "user_id": info.user_id,

        "age": info.age,
        "gender": info.gender,
        "transport": info.transport,  
        "budget": info.budget,
        "purpose": info.purpose,  
        "type": info.type,  
        "num": info.num,  

        "decide_place": info.decide_place,
        "place": info.place,

        "decide_date": info.decide_date,
        "date_start": str(info.date_start) if info.date_start else None,
        "date_end": str(info.date_end) if info.date_end else None,
        
        "decide_span": info.decide_span,
        "span_approx": info.span_approx,  
        "span_month": info.span_month,
        "span_week": info.span_week,
        "span_day": info.span_day,
        
        "infodetail": {
            "detail_purpose": info_detail.detail_purpose if info_detail else None,
            "interest": info_detail.interest if info_detail else None,
            "special_place": info_detail.special_place if info_detail else None,
            "religion": info_detail.religion if info_detail else None,
            "consideration": info_detail.consideration if info_detail else None,
        } if info_detail else None
    }
    return jsonify(result), 200
