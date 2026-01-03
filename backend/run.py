"""
Personal Financial Management Platform
個人財務管理平台  主程式入口

參考 Firefly III 開源架構設計

功能：
（一）財務管理功能
1. 個人日常支出管理
   - 透過使用者自行輸入支出項目來記錄每日、每月的消費情況
   - 透過關鍵字、歷史數據與使用者習慣進行分類
   - 更新各類別支出與預算狀態

2. 目標追蹤與儲蓄管理
   - 管理使用者的短期與中期財務目標
   - 計算各目標達成進度，提供清楚的進度報告
   - 根據使用者可支配金額與消費習慣生成可行策略
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# 完整的 CORS 設定
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 手動處理 OPTIONS 請求
@app.before_request
def handle_preflight():
    from flask import request
    if request.method == "OPTIONS":
        from flask import make_response
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response
    
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# 設定 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func, text

# 載入環境變數
load_dotenv()

# ========================================
# 資料庫設定 (參考 Firefly III 架構)
# ========================================
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def get_database_url():
    """建立資料庫連接 URL"""
    db_user = os.getenv('DB_USER', 'emily200008')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'bookkeeping')
    
    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"

# ========================================
# 關鍵字分類對照表 (參考 Firefly III Rules Engine)
# ========================================
KEYWORD_CATEGORY_MAP = {
    # 食物飲料 (1)
    '早餐': 1, '午餐': 1, '晚餐': 1, '飲料': 1, '咖啡': 1, '星巴克': 1,
    '麥當勞': 1, '肯德基': 1, '便當': 1, '小吃': 1, '餐廳': 1, '外送': 1,
    'ubereats': 1, 'foodpanda': 1, '超市': 1, '全聯': 1, '7-11': 1,
    
    # 交通 (2)
    '捷運': 2, '公車': 2, '計程車': 2, 'uber': 2, '高鐵': 2, '火車': 2,
    '加油': 2, '停車': 2, '機車': 2, '汽車': 2, 'youbike': 2,
    
    # 購物 (3)
    '衣服': 3, '鞋子': 3, '包包': 3, '網購': 3, 'pchome': 3, 'momo': 3,
    '蝦皮': 3, '百貨': 3, 'uniqlo': 3, 'zara': 3,
    
    # 娛樂 (4)
    '電影': 4, '遊戲': 4, 'netflix': 4, 'spotify': 4, '演唱會': 4,
    'ktv': 4, '書': 4, '漫畫': 4,
    
    # 帳單 (5)
    '電費': 5, '水費': 5, '瓦斯': 5, '網路': 5, '手機': 5, '電話費': 5,
    '房租': 5, '管理費': 5,
    
    # 醫療 (6)
    '看診': 6, '醫院': 6, '診所': 6, '藥': 6, '牙醫': 6, '健檢': 6,
    
    # 教育 (7)
    '學費': 7, '課程': 7, '補習': 7, '書籍': 7, '文具': 7,
    
    # 生活必需 (37) - 新增
    '衛生紙': 37, '洗衣精': 37, '沐浴乳': 37, '洗髮精': 37, '牙膏': 37,
    '日用品': 37, '生活用品': 37, '家用': 37, '清潔': 37, '廚房': 37,
    
    # 投資支出 (38) - 新增
    '股票': 38, '基金': 38, '定存': 38, 'etf': 38, '投資': 38,
    '證券': 38, '期貨': 38, '外幣': 38,
    
    # 收入關鍵字
    '薪水': 9, '薪資': 9, '工資': 9, '獎金': 9,
    '股利': 10, '利息': 10, '投資收益': 10,
    '兼職': 11, '接案': 11, '外快': 11,'家教': 11,
}

# 金額區間分類（當關鍵字無法判斷時使用）
AMOUNT_CATEGORY_RULES = [
    (20, 80, 1),      # 20-80 元 → 食物飲料（飲料、小點心）
    (80, 200, 1),     # 80-200 元 → 食物飲料（正餐）
    (15, 50, 2),      # 15-50 元 → 交通（捷運、公車）
]

def auto_categorize(description, amount=None):
    """
    自動分類功能 (參考 Firefly III Rules Engine)
    分類邏輯優先順序：
    1. 關鍵字比對
    2. 金額區間判斷
    3. 歷史紀錄相似度（TODO: 需要 app context）
    """
    description_lower = description.lower()
    
    # 1. 關鍵字比對
    for keyword, category_id in KEYWORD_CATEGORY_MAP.items():
        if keyword in description_lower:
            return category_id
    
    # 2. 金額區間判斷
    if amount is not None:
        for min_amt, max_amt, category_id in AMOUNT_CATEGORY_RULES:
            if min_amt <= amount <= max_amt:
                return category_id
    
    return None  # 無法自動分類

# ========================================
# 建立 Flask App
# ========================================
def create_app():
    app = Flask(__name__)
    
    # 設定
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False  # 支援中文顯示
    
    # 啟用 CORS

    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
    # 初始化資料庫
    db.init_app(app)
    
    
    # 首頁路由
    
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Personal Financial Management Platform',
            'version': '1.0.0',
            'description': '個人財務管理平台 API',
            'features': {
                '財務管理': {
                    '日常支出管理': [
                        '記錄每日、每月消費',
                        '自動關鍵字分類',
                        '預算狀態追蹤'
                    ],
                    '目標追蹤與儲蓄管理': [
                        '短期與中期財務目標',
                        '進度報告與計算',
                        '動態調整建議'
                    ]
                }
            },
            'endpoints': {
                'accounts': '/api/accounts',
                'categories': '/api/categories',
                'transactions': '/api/transactions',
                'budgets': '/api/budgets',
                'goals': '/api/goals',
                'reports': '/api/reports',
                'suggestions': '/api/suggestions'
            }
        })
    
    
    @app.route('/api/accounts', methods=['GET'])
    def get_accounts():
        """取得所有帳戶"""
        result = db.session.execute(text('SELECT * FROM accounts WHERE is_active = true'))
        accounts = []
        for row in result:
            accounts.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'balance': float(row[3]) if row[3] else 0,
                'currency': row[4],
                'description': row[5]
            })
        return jsonify(accounts)
    
    @app.route('/api/accounts', methods=['POST'])
    def create_account():
        """建立新帳戶"""
        data = request.get_json()
        
        db.session.execute(text('''
            INSERT INTO accounts (name, type, balance, currency, description)
            VALUES (:name, :type, :balance, :currency, :description)
        '''), {
            'name': data['name'],
            'type': data.get('type', 'checking'),
            'balance': data.get('balance', 0),
            'currency': data.get('currency', 'TWD'),
            'description': data.get('description', '')
        })
        db.session.commit()
        
        return jsonify({'message': '帳戶建立成功'}), 201
    
    @app.route('/api/accounts/<int:id>', methods=['PUT'])
    def update_account(id):
        """更新帳戶"""
        data = request.get_json()
        
        db.session.execute(text('''
            UPDATE accounts 
            SET name = :name, type = :type, balance = :balance, 
                currency = :currency, description = :description,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        '''), {
            'id': id,
            'name': data['name'],
            'type': data.get('type', 'checking'),
            'balance': data.get('balance', 0),
            'currency': data.get('currency', 'TWD'),
            'description': data.get('description', '')
        })
        db.session.commit()
        
        return jsonify({'message': '帳戶更新成功'})
    
    @app.route('/api/accounts/<int:id>', methods=['DELETE'])
    def delete_account(id):
        """刪除帳戶（軟刪除）"""
        db.session.execute(text('''
            UPDATE accounts SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        '''), {'id': id})
        db.session.commit()
        
        return jsonify({'message': '帳戶已刪除'})
    
    # 分類管理 API (參考 Firefly III Categories)
    
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        """取得所有分類"""
        category_type = request.args.get('type')
        
        if category_type:
            result = db.session.execute(text(
                'SELECT * FROM categories WHERE is_active = true AND type = :type'
            ), {'type': category_type})
        else:
            result = db.session.execute(text(
                'SELECT * FROM categories WHERE is_active = true'
            ))
        
        categories = []
        for row in result:
            categories.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'parent_id': row[3],
                'color': row[4],
                'icon': row[5],
                'description': row[6]
            })
        return jsonify(categories)
    
    @app.route('/api/categories', methods=['POST'])
    def create_category():
        """建立新分類"""
        data = request.get_json()
        
        db.session.execute(text('''
            INSERT INTO categories (name, type, color, icon, description)
            VALUES (:name, :type, :color, :icon, :description)
        '''), {
            'name': data['name'],
            'type': data['type'],
            'color': data.get('color', '#808080'),
            'icon': data.get('icon', '📁'),
            'description': data.get('description', '')
        })
        db.session.commit()
        
        return jsonify({'message': '分類建立成功'}), 201
    
    # 交易記錄 API - 日常支出管理 參考 Firefly III Transactions

    @app.route('/api/transactions', methods=['GET'])
    def get_transactions():
        """
        取得所有交易記錄
        支援篩選：type, account_id, category_id, start_date, end_date
        """
        query = 'SELECT * FROM transactions WHERE 1=1'
        params = {}
        
        if request.args.get('type'):
            query += ' AND type = :type'
            params['type'] = request.args.get('type')
        
        if request.args.get('account_id'):
            query += ' AND account_id = :account_id'
            params['account_id'] = request.args.get('account_id')
        
        if request.args.get('category_id'):
            query += ' AND category_id = :category_id'
            params['category_id'] = request.args.get('category_id')
        
        if request.args.get('start_date'):
            query += ' AND date >= :start_date'
            params['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            query += ' AND date <= :end_date'
            params['end_date'] = request.args.get('end_date')
        
        query += ' ORDER BY date DESC, id DESC'
        
        result = db.session.execute(text(query), params)
        transactions = []
        for row in result:
            transactions.append({
                'id': row[0],
                'account_id': row[1],
                'category_id': row[2],
                'date': str(row[3]) if row[3] else None,
                'description': row[4],
                'amount': float(row[5]) if row[5] else 0,
                'type': row[6],
                'notes': row[7]
            })
        return jsonify(transactions)
    
    @app.route('/api/transactions', methods=['POST'])
    def create_transaction():
        """
        建立新交易記錄
        功能：透過使用者自行輸入支出項目來記錄消費
        自動分類：透過關鍵字進行分類
        """
        data = request.get_json()
        
        # 自動分類功能
        category_id = data.get('category_id')
        if not category_id:
            category_id = auto_categorize(data['description'], data.get('amount'))
            if not category_id:
                # 預設分類：其他支出(8) 或 其他收入(12)
                category_id = 8 if data['type'] == 'expense' else 12
        
        db.session.execute(text('''
            INSERT INTO transactions (account_id, category_id, date, description, amount, type, notes)
            VALUES (:account_id, :category_id, :date, :description, :amount, :type, :notes)
        '''), {
            'account_id': data['account_id'],
            'category_id': category_id,
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'description': data['description'],
            'amount': data['amount'],
            'type': data['type'],
            'notes': data.get('notes', '')
        })
        db.session.commit()
        
        # 更新帳戶餘額
        if data['type'] == 'expense':
            db.session.execute(text('''
                UPDATE accounts SET balance = balance - :amount, updated_at = CURRENT_TIMESTAMP
                WHERE id = :account_id
            '''), {'amount': data['amount'], 'account_id': data['account_id']})
        else:
            db.session.execute(text('''
                UPDATE accounts SET balance = balance + :amount, updated_at = CURRENT_TIMESTAMP
                WHERE id = :account_id
            '''), {'amount': data['amount'], 'account_id': data['account_id']})
        db.session.commit()
        
        return jsonify({
            'message': '交易記錄建立成功',
            'auto_category_id': category_id
        }), 201
    
    @app.route('/api/transactions/<int:id>', methods=['DELETE'])
    def delete_transaction(id):
        """刪除交易記錄"""
        db.session.execute(text('DELETE FROM transactions WHERE id = :id'), {'id': id})
        db.session.commit()
        return jsonify({'message': '交易記錄已刪除'})
    
    @app.route('/api/transactions/summary', methods=['GET'])
    def get_transaction_summary():
        """
        取得交易摘要
        功能：即時更新數據，顯示每日、每月的消費情況
        """
        # 取得時間範圍
        start_date = request.args.get('start_date', 
            (datetime.now().replace(day=1)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', 
            datetime.now().strftime('%Y-%m-%d'))
        
        # 總收入
        income_result = db.session.execute(text('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income' AND date BETWEEN :start AND :end
        '''), {'start': start_date, 'end': end_date})
        total_income = float(income_result.scalar())
        
        # 總支出
        expense_result = db.session.execute(text('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense' AND date BETWEEN :start AND :end
        '''), {'start': start_date, 'end': end_date})
        total_expense = float(expense_result.scalar())
        
        # 各類別支出統計
        category_result = db.session.execute(text('''
            SELECT c.name, c.icon, COALESCE(SUM(t.amount), 0) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense' AND t.date BETWEEN :start AND :end
            GROUP BY c.id, c.name, c.icon
            ORDER BY total DESC
        '''), {'start': start_date, 'end': end_date})
        
        categories_breakdown = []
        for row in category_result:
            categories_breakdown.append({
                'category': row[0],
                'icon': row[1],
                'amount': float(row[2])
            })
        
        return jsonify({
            'period': {
                'start': start_date,
                'end': end_date
            },
            'total_income': total_income,
            'total_expense': total_expense,
            'net': total_income - total_expense,
            'categories_breakdown': categories_breakdown
        })
    

    # 預算管理 API (參考 Firefly III Budgets)
    
    @app.route('/api/budgets', methods=['GET'])
    def get_budgets():
        """
        取得所有預算及使用狀態
        功能：自動處理過期與達標狀態
        """
        try:
            today = datetime.now().date()
            
            # 查詢所有 active 預算
            result = db.session.execute(text('''
                SELECT b.id, b.category_id, b.name, b.amount, b.period, 
                       b.start_date, b.end_date, b.is_active, b.status,
                       c.name as category_name, c.icon as category_icon,
                       COALESCE((
                           SELECT SUM(t.amount) 
                           FROM transactions t 
                           WHERE t.category_id = b.category_id 
                           AND t.type = 'expense'
                           AND t.date >= b.start_date
                           AND (b.end_date IS NULL OR t.date <= b.end_date)
                       ), 0) as spent
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                WHERE b.is_active = true
                ORDER BY 
                    CASE WHEN b.end_date IS NULL THEN 1 ELSE 0 END,
                    b.end_date ASC
            '''))
            
            budgets = []
            ids_to_delete = []  # 過期未達標，要刪除的
            ids_to_complete = []  # 達標的
            
            for row in result:
                budget_id = row[0]
                budget_amount = float(row[3]) if row[3] else 0
                spent = float(row[11]) if row[11] else 0
                remaining = budget_amount - spent
                usage_percent = (spent / budget_amount * 100) if budget_amount > 0 else 0
                end_date = row[6]
                
                # 計算剩餘天數
                days_remaining = None
                is_expired = False
                if end_date:
                    if isinstance(end_date, str):
                        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    days_remaining = (end_date - today).days
                    is_expired = days_remaining < 0
                
                # 判斷狀態
                is_completed = usage_percent >= 100 or spent >= budget_amount
                
                if is_expired and not is_completed:
                    # 過期未達標 → 加入刪除清單
                    ids_to_delete.append(budget_id)
                    continue  # 不加入回傳列表
                
                if is_completed:
                    # 達標 → 標記為 completed
                    ids_to_complete.append(budget_id)
                    status = 'completed'
                elif is_expired:
                    status = 'expired'
                elif usage_percent > 80:
                    status = 'warning'
                else:
                    status = 'ok'
                
                budgets.append({
                    'id': budget_id,
                    'category_id': row[1],
                    'name': row[2],
                    'amount': budget_amount,
                    'period': row[4],
                    'start_date': str(row[5]) if row[5] else None,
                    'end_date': str(row[6]) if row[6] else None,
                    'category_name': row[9],
                    'category_icon': row[10],
                    'spent': spent,
                    'remaining': remaining,
                    'usage_percent': round(usage_percent, 2),
                    'days_remaining': days_remaining,
                    'status': status
                })
            
            # 刪除過期未達標的預算
            if ids_to_delete:
                db.session.execute(text(
                    'DELETE FROM budgets WHERE id IN :ids'
                ), {'ids': tuple(ids_to_delete)})
                db.session.commit()
            
            # 更新達標預算的狀態
            if ids_to_complete:
                db.session.execute(text(
                    'UPDATE budgets SET status = :status WHERE id IN :ids'
                ), {'status': 'completed', 'ids': tuple(ids_to_complete)})
                db.session.commit()
            
            return jsonify(budgets)
        except Exception as e:
            print(f'取得預算錯誤: {e}')
            return jsonify({'error': str(e)}), 500
    @app.route('/api/budgets/<int:id>', methods=['DELETE'])
    def delete_budget(id):
        """刪除預算"""
        try:
            db.session.execute(text('DELETE FROM budgets WHERE id = :id'), {'id': id})
            db.session.commit()
            return jsonify({'message': '預算已刪除'})
        except Exception as e:
            print(f'刪除預算錯誤: {e}')
            return jsonify({'error': str(e)}), 500
        
    @app.route('/api/budgets', methods=['POST'])
    @app.route('/api/budgets', methods=['POST'])
    def create_budget():
        """建立新預算"""
        try:
            data = request.get_json()
            
            db.session.execute(text('''
                INSERT INTO budgets (category_id, name, amount, period, start_date, end_date)
                VALUES (:category_id, :name, :amount, :period, :start_date, :end_date)
            '''), {
                'category_id': data['category_id'],
                'name': data['name'],
                'amount': data['amount'],
                'period': data.get('period', 'monthly'),
                'start_date': data['start_date'],
                'end_date': data.get('end_date')
            })
            db.session.commit()
            
            return jsonify({'message': '預算建立成功'}), 201
        except Exception as e:
            print(f'新增預算錯誤: {e}')
            return jsonify({'error': str(e)}), 500
    
    # 財務目標 API - 目標追蹤與儲蓄管理(參考 Firefly III Piggy Banks)
    
    @app.route('/api/goals', methods=['GET'])
    def get_goals():
        """
        取得所有財務目標
        功能：管理使用者的短期與中期財務目標
        """
        status = request.args.get('status')
        
        if status:
            result = db.session.execute(text(
                'SELECT * FROM financial_goals WHERE status = :status ORDER BY priority DESC'
            ), {'status': status})
        else:
            result = db.session.execute(text(
                'SELECT * FROM financial_goals ORDER BY priority DESC'
            ))
        
        goals = []
        for row in result:
            target = float(row[2]) if row[2] else 0
            current = float(row[3]) if row[3] else 0
            progress = (current / target * 100) if target > 0 else 0
            
            # 計算預估達成日期
            days_remaining = None
            if row[4] and row[6] == 'in_progress':  # deadline exists and in progress
                deadline = row[4]
                if isinstance(deadline, str):
                    deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                days_remaining = (deadline - datetime.now().date()).days
            
            goals.append({
                'id': row[0],
                'name': row[1],
                'target_amount': target,
                'current_amount': current,
                'deadline': str(row[4]) if row[4] else None,
                'priority': row[5],
                'status': row[6],
                'description': row[7],
                'progress': round(progress, 2),
                'remaining_amount': target - current,
                'days_remaining': days_remaining
            })
        
        return jsonify(goals)
    
    @app.route('/api/goals', methods=['POST'])
    def create_goal():
        """
        建立新財務目標
        功能：設定短期與中期財務目標（如每月儲蓄、旅行基金）
        """
        data = request.get_json()
        
        db.session.execute(text('''
            INSERT INTO financial_goals (name, target_amount, current_amount, deadline, priority, description)
            VALUES (:name, :target_amount, :current_amount, :deadline, :priority, :description)
        '''), {
            'name': data['name'],
            'target_amount': data['target_amount'],
            'current_amount': data.get('current_amount', 0),
            'deadline': data.get('deadline'),
            'priority': data.get('priority', 3),
            'description': data.get('description', '')
        })
        db.session.commit()
        
        return jsonify({'message': '財務目標建立成功'}), 201
    
    @app.route('/api/goals/<int:id>', methods=['PUT'])
    def update_goal(id):
        """更新財務目標"""
        data = request.get_json()
        
        # 取得目前目標
        result = db.session.execute(text(
            'SELECT target_amount, current_amount FROM financial_goals WHERE id = :id'
        ), {'id': id})
        row = result.fetchone()
        
        current_amount = data.get('current_amount', float(row[1]) if row[1] else 0)
        target_amount = data.get('target_amount', float(row[0]) if row[0] else 0)
        
        # 自動檢查是否達成目標
        status = data.get('status', 'in_progress')
        if current_amount >= target_amount:
            status = 'completed'
        
        db.session.execute(text('''
            UPDATE financial_goals 
            SET name = :name, target_amount = :target_amount, current_amount = :current_amount,
                deadline = :deadline, priority = :priority, status = :status, 
                description = :description, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        '''), {
            'id': id,
            'name': data.get('name'),
            'target_amount': target_amount,
            'current_amount': current_amount,
            'deadline': data.get('deadline'),
            'priority': data.get('priority', 3),
            'status': status,
            'description': data.get('description', '')
        })
        db.session.commit()
        
        return jsonify({'message': '財務目標更新成功', 'status': status})
    
    @app.route('/api/goals/<int:id>/add-money', methods=['POST'])
    def add_money_to_goal(id):
        """
        為目標增加存款
        功能：追蹤儲蓄進度
        """
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        # 更新目標金額
        db.session.execute(text('''
            UPDATE financial_goals 
            SET current_amount = current_amount + :amount,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        '''), {'id': id, 'amount': amount})
        
        # 檢查是否達成目標
        result = db.session.execute(text(
            'SELECT target_amount, current_amount FROM financial_goals WHERE id = :id'
        ), {'id': id})
        row = result.fetchone()
        
        if row and float(row[1]) >= float(row[0]):
            db.session.execute(text('''
                UPDATE financial_goals SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'id': id})
        
        db.session.commit()
        
        return jsonify({'message': f'已新增 ${amount} 到目標'})
    
    @app.route('/api/goals/<int:id>/progress', methods=['GET'])
    def get_goal_progress(id):
        """
        取得目標進度報告
        功能：計算各目標達成進度，提供清楚的進度報告
        """
        result = db.session.execute(text(
            'SELECT * FROM financial_goals WHERE id = :id'
        ), {'id': id})
        row = result.fetchone()
        
        if not row:
            return jsonify({'error': '目標不存在'}), 404
        
        target = float(row[2]) if row[2] else 0
        current = float(row[3]) if row[3] else 0
        progress = (current / target * 100) if target > 0 else 0
        remaining = target - current
        
        # 計算每日/每週/每月需要存多少
        daily_needed = 0
        weekly_needed = 0
        monthly_needed = 0
        
        if row[4]:  # deadline exists
            deadline = row[4]
            if isinstance(deadline, str):
                deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
            days_remaining = (deadline - datetime.now().date()).days
            
            if days_remaining > 0:
                daily_needed = remaining / days_remaining
                weekly_needed = remaining / (days_remaining / 7)
                monthly_needed = remaining / (days_remaining / 30)
        
        return jsonify({
            'id': row[0],
            'name': row[1],
            'target_amount': target,
            'current_amount': current,
            'remaining_amount': remaining,
            'progress_percent': round(progress, 2),
            'deadline': str(row[4]) if row[4] else None,
            'status': row[6],
            'recommendations': {
                'daily_saving_needed': round(daily_needed, 2),
                'weekly_saving_needed': round(weekly_needed, 2),
                'monthly_saving_needed': round(monthly_needed, 2)
            }
        })
    
    
    # 報表與分析 API
    
    @app.route('/api/reports/monthly', methods=['GET'])
    def get_monthly_report():
        """
        取得月度報表
        功能：記錄每月的消費情況
        """
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        start_date = f'{year}-{month:02d}-01'
        if month == 12:
            end_date = f'{int(year)+1}-01-01'
        else:
            end_date = f'{year}-{int(month)+1:02d}-01'
        
        # 每日支出
        daily_result = db.session.execute(text('''
            SELECT date, SUM(amount) as total
            FROM transactions
            WHERE type = 'expense' AND date >= :start AND date < :end
            GROUP BY date
            ORDER BY date
        '''), {'start': start_date, 'end': end_date})
        
        daily_expenses = []
        for row in daily_result:
            daily_expenses.append({
                'date': str(row[0]),
                'amount': float(row[1])
            })
        
        # 類別統計
        category_result = db.session.execute(text('''
            SELECT c.name, c.icon, c.color, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense' AND t.date >= :start AND t.date < :end
            GROUP BY c.id, c.name, c.icon, c.color
            ORDER BY total DESC
        '''), {'start': start_date, 'end': end_date})
        
        categories = []
        for row in category_result:
            categories.append({
                'name': row[0],
                'icon': row[1],
                'color': row[2],
                'amount': float(row[3])
            })
        
        return jsonify({
            'year': year,
            'month': month,
            'daily_expenses': daily_expenses,
            'categories': categories
        })
    

    # 智慧建議 API
   
    @app.route('/api/suggestions', methods=['GET'])
    def get_suggestions():
        """
        取得財務建議
        功能：根據使用者可支配金額與消費習慣生成可行策略，
              並提供動態調整建議
        """
        suggestions = []
        
        # 1. 分析本月支出
        today = datetime.now()
        start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        
        # 本月總支出
        expense_result = db.session.execute(text('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense' AND date >= :start
        '''), {'start': start_of_month})
        monthly_expense = float(expense_result.scalar())
        
        # 本月總收入
        income_result = db.session.execute(text('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income' AND date >= :start
        '''), {'start': start_of_month})
        monthly_income = float(income_result.scalar())
        
        # 計算可支配金額
        disposable = monthly_income - monthly_expense
        days_passed = today.day
        days_in_month = 30
        days_remaining = days_in_month - days_passed
        
        # 2. 分析預算狀態
        budget_result = db.session.execute(text('''
            SELECT b.name, b.amount, c.name as category_name,
                   COALESCE((
                       SELECT SUM(t.amount) FROM transactions t 
                       WHERE t.category_id = b.category_id 
                       AND t.type = 'expense'
                       AND t.date >= b.start_date
                   ), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.is_active = true
        '''))
        
        for row in budget_result:
            budget_amount = float(row[1])
            spent = float(row[3])
            usage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            if usage > 100:
                suggestions.append({
                    'type': 'warning',
                    'category': '預算超支',
                    'message': f'{row[2]} 的預算已超支 {usage-100:.1f}%，建議減少此類支出'
                })
            elif usage > 80:
                suggestions.append({
                    'type': 'caution',
                    'category': '預算警告',
                    'message': f'{row[2]} 的預算已使用 {usage:.1f}%，請注意控制支出'
                })
        
        # 3. 分析儲蓄目標
        goal_result = db.session.execute(text('''
            SELECT name, target_amount, current_amount, deadline
            FROM financial_goals
            WHERE status = 'in_progress'
        '''))
        
        for row in goal_result:
            target = float(row[1])
            current = float(row[2])
            remaining = target - current
            
            if row[3]:  # has deadline
                deadline = row[3]
                if isinstance(deadline, str):
                    deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
                days_to_deadline = (deadline - today.date()).days
                
                if days_to_deadline > 0:
                    daily_needed = remaining / days_to_deadline
                    weekly_needed = daily_needed * 7
                    
                    if disposable > 0 and days_remaining > 0:
                        daily_available = disposable / days_remaining
                        
                        if daily_available >= daily_needed:
                            suggestions.append({
                                'type': 'success',
                                'category': '儲蓄建議',
                                'message': f'目標「{row[0]}」進度良好！建議每日存 ${daily_needed:.0f}，您目前每日可存 ${daily_available:.0f}'
                            })
                        else:
                            suggestions.append({
                                'type': 'info',
                                'category': '儲蓄調整',
                                'message': f'目標「{row[0]}」需要每日存 ${daily_needed:.0f}，建議提高每週儲蓄額或調整目標日期'
                            })
        
        # 4. 一般建議
        if monthly_income > 0:
            savings_rate = (disposable / monthly_income * 100) if disposable > 0 else 0
            
            if savings_rate < 10:
                suggestions.append({
                    'type': 'warning',
                    'category': '儲蓄率偏低',
                    'message': f'本月儲蓄率僅 {savings_rate:.1f}%，建議目標至少 20%'
                })
            elif savings_rate >= 30:
                suggestions.append({
                    'type': 'success',
                    'category': '儲蓄表現優異',
                    'message': f'本月儲蓄率達 {savings_rate:.1f}%，表現優異！'
                })
        
        return jsonify({
            'summary': {
                'monthly_income': monthly_income,
                'monthly_expense': monthly_expense,
                'disposable': disposable,
                'days_remaining': days_remaining
            },
            'suggestions': suggestions
        })
    
    # 健康檢查
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'database': 'connected'})
    
    return app

# 建立 app 實例
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Personal Financial Management Platform                      ║
    ║   個人財務管理平台 v1.0                                        ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   Server: http://localhost:{port}                               ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   功能：                                                       ║
    ║   1. 日常支出管理 - 自動分類、即時更新                          ║
    ║   2. 目標追蹤 - 進度報告、達成建議                              ║
    ║   3. 預算管理 - 狀態追蹤、超支警告                              ║
    ║   4. 智慧建議 - 動態調整、儲蓄策略                              ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║   API Endpoints:                                              ║
    ║   • /api/accounts      - 帳戶管理                              ║
    ║   • /api/categories    - 分類管理                              ║
    ║   • /api/transactions  - 交易記錄 + 自動分類                    ║
    ║   • /api/budgets       - 預算管理 + 狀態追蹤                    ║
    ║   • /api/goals         - 財務目標 + 進度報告                    ║
    ║   • /api/reports       - 報表分析                              ║
    ║   • /api/suggestions   - 智慧建議                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)