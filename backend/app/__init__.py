"""
Flask 應用程式初始化
"""
"""
from flask import Flask
from flask_cors import CORS
from app.database import init_db

def create_app():
   
    app = Flask(__name__)
    
    # 啟用 CORS（讓前端可以呼叫 API）
    CORS(app)
    
    # 初始化資料庫
    init_db(app)
    
    return app
    """