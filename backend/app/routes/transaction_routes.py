"""
Transaction API 路由
處理交易記錄的 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.transaction import Transaction
from datetime import datetime

# 建立 Blueprint
transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transaction_bp.route('', methods=['GET'])
def get_transactions():
    """
    取得所有交易記錄
    GET /api/transactions
    可選參數: type, account_id, category_id, start_date, end_date
    """
    query = Transaction.query
    
    # 篩選條件
    if request.args.get('type'):
        query = query.filter(Transaction.type == request.args.get('type'))
    
    if request.args.get('account_id'):
        query = query.filter(Transaction.account_id == request.args.get('account_id'))
    
    if request.args.get('category_id'):
        query = query.filter(Transaction.category_id == request.args.get('category_id'))
    
    if request.args.get('start_date'):
        start = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(Transaction.date >= start)
    
    if request.args.get('end_date'):
        end = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(Transaction.date <= end)
    
    # 按日期排序（最新的在前）
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return jsonify([t.to_dict() for t in transactions])

@transaction_bp.route('/<int:id>', methods=['GET'])
def get_transaction(id):
    """
    取得單一交易記錄
    GET /api/transactions/<id>
    """
    transaction = Transaction.query.get_or_404(id)
    return jsonify(transaction.to_dict())

@transaction_bp.route('', methods=['POST'])
def create_transaction():
    """
    建立新交易記錄
    POST /api/transactions
    """
    data = request.get_json()
    
    # 解析日期
    trans_date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.utcnow().date()
    
    transaction = Transaction(
        account_id=data['account_id'],
        category_id=data.get('category_id'),
        date=trans_date,
        description=data['description'],
        amount=data['amount'],
        type=data['type'],
        notes=data.get('notes')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify(transaction.to_dict()), 201

@transaction_bp.route('/<int:id>', methods=['PUT'])
def update_transaction(id):
    """
    更新交易記錄
    PUT /api/transactions/<id>
    """
    transaction = Transaction.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('date'):
        transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    transaction.account_id = data.get('account_id', transaction.account_id)
    transaction.category_id = data.get('category_id', transaction.category_id)
    transaction.description = data.get('description', transaction.description)
    transaction.amount = data.get('amount', transaction.amount)
    transaction.type = data.get('type', transaction.type)
    transaction.notes = data.get('notes', transaction.notes)
    
    db.session.commit()
    
    return jsonify(transaction.to_dict())

@transaction_bp.route('/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    """
    刪除交易記錄
    DELETE /api/transactions/<id>
    """
    transaction = Transaction.query.get_or_404(id)
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': '交易記錄已刪除'}), 200

@transaction_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    取得交易摘要（總收入、總支出）
    GET /api/transactions/summary
    """
    from sqlalchemy import func
    
    # 計算總收入
    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'income'
    ).scalar() or 0
    
    # 計算總支出
    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'expense'
    ).scalar() or 0
    
    return jsonify({
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net': float(total_income) - float(total_expense)
    })