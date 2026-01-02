"""
Personal Financial Management Platform
主程式入口
"""

import os
import sys

# 取得目前檔案的目錄路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# 載入環境變數
load_dotenv()

# ========== 資料庫設定 ==========
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def get_database_url():
    db_user = os.getenv('DB_USER', 'emily200008')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'bookkeeping')
    
    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"

# ========== 建立 Flask App ==========
def create_app():
    app = Flask(__name__)
    
    # 設定
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 啟用 CORS
    CORS(app)
    
    # 初始化資料庫
    db.init_app(app)
    
    # 首頁路由
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Personal Financial Management Platform',
            'version': '1.0.0',
            'description': '個人財務管理平台 API',
            'features': [
                '日常支出管理',
                '目標追蹤與儲蓄管理', 
                '預算管理'
            ],
            'endpoints': {
                'accounts': '/api/accounts',
                'categories': '/api/categories',
                'transactions': '/api/transactions',
                'budgets': '/api/budgets',
                'goals': '/api/goals'
            }
        })
    
    # 健康檢查
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})
    
    # 測試資料庫連線
    @app.route('/api/categories')
    def get_categories():
        try:
            result = db.session.execute(db.text('SELECT * FROM categories'))
            categories = []
            for row in result:
                categories.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'color': row[4],
                    'icon': row[5]
                })
            return jsonify(categories)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

# 建立 app 實例
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║   Personal Financial Management Platform              ║
    ║   個人財務管理平台                                     ║
    ╠═══════════════════════════════════════════════════════╣
    ║   Server running at: http://localhost:{port}            ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)