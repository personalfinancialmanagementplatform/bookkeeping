"""
Budget API 路由
處理預算的 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.budget import Budget
from app.models.transaction import Transaction
from datetime import datetime
from sqlalchemy import func

# 建立 Blueprint
budget_bp = Blueprint('budgets', __name__, url_prefix='/api/budgets')

@budget_bp.route('', methods=['GET'])
def get_budgets():
    """
    取得所有預算
    GET /api/budgets
    """
    budgets = Budget.query.filter(Budget.is_active == True).all()
    return jsonify([budget.to_dict() for budget in budgets])

@budget_bp.route('/<int:id>', methods=['GET'])
def get_budget(id):
    """
    取得單一預算（含使用狀況）
    GET /api/budgets/<id>
    """
    budget = Budget.query.get_or_404(id)
    
    # 計算此預算的已使用金額
    spent = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.category_id == budget.category_id,
        Transaction.type == 'expense',
        Transaction.date >= budget.start_date
    )
    
    if budget.end_date:
        spent = spent.filter(Transaction.date <= budget.end_date)
    
    spent_amount = spent.scalar() or 0
    
    result = budget.to_dict()
    result['spent'] = float(spent_amount)
    result['remaining'] = float(budget.amount) - float(spent_amount)
    result['usage_percent'] = round((float(spent_amount) / float(budget.amount)) * 100, 2) if budget.amount > 0 else 0
    
    return jsonify(result)

@budget_bp.route('', methods=['POST'])
def create_budget():
    """
    建立新預算
    POST /api/budgets
    """
    data = request.get_json()
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    
    budget = Budget(
        category_id=data['category_id'],
        name=data['name'],
        amount=data['amount'],
        period=data['period'],
        start_date=start_date,
        end_date=end_date
    )
    
    db.session.add(budget)
    db.session.commit()
    
    return jsonify(budget.to_dict()), 201

@budget_bp.route('/<int:id>', methods=['PUT'])
def update_budget(id):
    """
    更新預算
    PUT /api/budgets/<id>
    """
    budget = Budget.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('start_date'):
        budget.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    
    if data.get('end_date'):
        budget.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    budget.category_id = data.get('category_id', budget.category_id)
    budget.name = data.get('name', budget.name)
    budget.amount = data.get('amount', budget.amount)
    budget.period = data.get('period', budget.period)
    budget.is_active = data.get('is_active', budget.is_active)
    
    db.session.commit()
    
    return jsonify(budget.to_dict())

@budget_bp.route('/<int:id>', methods=['DELETE'])
def delete_budget(id):
    """
    刪除預算
    DELETE /api/budgets/<id>
    """
    budget = Budget.query.get_or_404(id)
    
    budget.is_active = False
    db.session.commit()
    
    return jsonify({'message': '預算已刪除'}), 200