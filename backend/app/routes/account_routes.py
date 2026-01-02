"""
Account API 路由
處理帳戶的 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.account import Account

# 建立 Blueprint
account_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

@account_bp.route('', methods=['GET'])
def get_accounts():
    """
    取得所有帳戶
    GET /api/accounts
    """
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])

@account_bp.route('/<int:id>', methods=['GET'])
def get_account(id):
    """
    取得單一帳戶
    GET /api/accounts/<id>
    """
    account = Account.query.get_or_404(id)
    return jsonify(account.to_dict())

@account_bp.route('', methods=['POST'])
def create_account():
    """
    建立新帳戶
    POST /api/accounts
    """
    data = request.get_json()
    
    account = Account(
        name=data['name'],
        type=data['type'],
        balance=data.get('balance', 0.00),
        currency=data.get('currency', 'TWD'),
        description=data.get('description')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify(account.to_dict()), 201

@account_bp.route('/<int:id>', methods=['PUT'])
def update_account(id):
    """
    更新帳戶
    PUT /api/accounts/<id>
    """
    account = Account.query.get_or_404(id)
    data = request.get_json()
    
    account.name = data.get('name', account.name)
    account.type = data.get('type', account.type)
    account.balance = data.get('balance', account.balance)
    account.currency = data.get('currency', account.currency)
    account.description = data.get('description', account.description)
    account.is_active = data.get('is_active', account.is_active)
    
    db.session.commit()
    
    return jsonify(account.to_dict())

@account_bp.route('/<int:id>', methods=['DELETE'])
def delete_account(id):
    """
    刪除帳戶
    DELETE /api/accounts/<id>
    """
    account = Account.query.get_or_404(id)
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': '帳戶已刪除'}), 200