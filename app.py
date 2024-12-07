from flask import Flask
from models import db
from config import Config
from routes import initialize_routes
from flask_cors import CORS
from routes.user_routes import user_bp
from routes.chatbot_routes import chat_bp
from routes.session_routes import session_bp
from routes.drawer_routes import drawer_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  

db.init_app(app)

# DB 초기화
with app.app_context():
    db.create_all()

# 라우트 초기화
initialize_routes(app)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(session_bp, url_prefix = '/sesh')
app.register_blueprint(chat_bp, url_prefix='/llm')
app.register_blueprint(drawer_bp, url_prefix='/drawer')

if __name__ == '__main__':
    app.run(debug=True)