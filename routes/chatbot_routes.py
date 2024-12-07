from flask import Blueprint, request, jsonify
from models import db, Session, Message, Sender, Info, InfoDetail
from datetime import datetime
from chatbot import tuning_run
from user_format import basic_format, detail_format
import re
from summary import extract_summary
from sqlalchemy.sql import exists

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("content")
        print(user_message)

        SessionID = data.get('session_id')
        InfoID = data.get('info_id')
        print(f'session: {SessionID}, info: {InfoID}')

        # Session의 첫 메시지인지 확인
        exists_query = db.session.query(exists().where(Message.session_id == SessionID)).scalar()
        print(exists_query)

        info_dict = {}
        info_dict[SessionID] = {}
        info = Info.query.filter_by(info_id=InfoID).first()

        user_info = {
            'age' : info.age,
            'gender' : info.gender,
            'transport' : info.transport,
            'budget' : info.budget,
            'purpose' : info.purpose,
            'type' : info.type,
            'num' : info.num,
            'decide_place' : info.decide_place,
            'place' : info.place,
            'decide_date' : info.decide_date,
            'date_start' : info.date_start,
            'date_end' : info.date_end,
            'decide_span' : info.decide_span,
            'span_approx' : info.span_approx,
            'span_month' : info.span_month,
            'span_week' : info.span_week,
            'span_day' : info.span_day
        }
        info_dict[SessionID]['info'] = user_info

        info_detail = InfoDetail.query.filter_by(info_id=InfoID).first()
        user_detail_info = {
            'detail_purpose' : info_detail.detail_purpose,
            'interest' : info_detail.interest,
            'special_place' : info_detail.special_place,
            'religion' : info_detail.religion,
            'consideration' : info_detail.consideration
        }
        info_dict[SessionID]['info_detail'] = user_detail_info

        info = info_dict[SessionID]
        basic = info['info']
        detail = info['info_detail']

        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        
        user_information = basic_format(basic)
        user_detail = detail_format(detail)
        
        try:
            usr = Message(session_id = SessionID, 
                        sender = Sender.question, 
                        content = user_message, 
                        timestamp = datetime.now())
            db.session.add(usr)
            db.session.commit()
            print('check')
                        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Cannot put in Message DB - usr'})

        bot_message = tuning_run(user_information, user_detail, user_message)
        #bot_message = '지피티 4옴니의 토큰 개수 제한이 두려워서 만든 테스트용 메시지입니다. '

        if "```" in bot_message:
            bot_message = bot_message.replace("```", "").strip()
            
        print(bot_message)

        # To extract message_id
        prev = str(usr)
        print(prev)
        number = re.search(r'\d+', prev)
        if number:
            prev_id = int(number.group())
        else:
            return jsonify({'error' : 'Fail to extract number'})
        print(prev_id)
        
        # DB에 parent_id까지 해서 bot row update
        try:
            bot = Message(session_id = SessionID, 
                          parent_id = prev_id,
                          sender = Sender.answer, 
                          content = bot_message, 
                          timestamp = datetime.now())
            
            db.session.add(bot)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error: Cannot put in Message DB - bot'})
        
        # 첫 메시지일 때만 bot 요약 넣기
        if exists_query is False:
            print('Put summary')
            summary = extract_summary(bot_message)
            try:
                session_row = Session.query.filter_by(session_id=SessionID, info_id=InfoID).first()
                session_row.session_title = summary  
                db.session.commit()
            
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Cannot update Session DB with summary: {str(e)}'}), 500
            
        # bot update까지 된 시간 이후로 계속 Session의 end time update
        try:
            print('Update End time')
            session_row = Session.query.filter_by(session_id=SessionID, info_id=InfoID).first()
            session_row.session_end = datetime.now()
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Cannot update end time'})


        return jsonify({"content": bot_message})

    except Exception as e:
        
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    session_id = int(request.args.get('session_id'))
    print(f'session ID: {session_id}')

    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    try:
        messages = Message.query.filter_by(session_id=session_id).all()
        print(messages)

        message_num = []
        for mess in messages:
            mess = str(mess)
            num = re.search(r'\d+', mess)
            if num:
                message_num.append(int(num.group()))
        
        print(f'mess_num : {message_num}')

        message_list = []
        for num in message_num:
            mess = Message.query.filter_by(message_id=num).first()
            temp_dict = {}
            temp_dict['content'] = mess.content
            temp_dict['sender'] = mess.sender.value
            message_list.append(temp_dict)
        print(message_list)

        return jsonify(message_list), 200
    
    except Exception as e:
        return jsonify({'error': f'Error occured: {str(e)}'}), 500
    
@chat_bp.route('/ids', methods = ['GET'])
def get_ids():
    user_id = int(request.args.get('user_id'))
    print(f'User ID: {user_id}')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    try:
        session = Session.query.filter_by(user_id=user_id).order_by(Session.session_end.desc()).first()
        session = str(session)
        num = re.search(r'\d+', session)
        num = int(num.group())
        print(num)

        ids_list = []
        temp_dict = {}
        target = Session.query.filter_by(session_id = num).first()
        temp_dict['info_id'] = target.info_id
        temp_dict['session_id'] = target.session_id
        temp_dict['session_title'] = target.session_title
        ids_list.append(temp_dict)
        print(ids_list)
    
        return jsonify(ids_list), 200

    except Exception as e:
         return jsonify({'error': f'Error occured: {str(e)}'}), 500