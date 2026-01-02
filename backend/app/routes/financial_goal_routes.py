"""
FinancialGoal API 路由
處理財務目標的 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.financial_goal import FinancialGoal
from datetime import datetime

# 建立 Blueprint
financial_goal_bp = Blueprint('financial_goals', __name__, url_prefix='/api/goals')

@financial_goal_bp.route('', methods=['GET'])
def get_goals():
    """
    取得所有財務目標
    GET /api/goals
    可選參數: status (in_progress/completed/cancelled)
    """
    query = FinancialGoal.query
    
    if request.args.get('status'):
        query = query.filter(FinancialGoal.status == request.args.get('status'))
    
    goals = query.order_by(FinancialGoal.priority.desc()).all()
    
    return jsonify([goal.to_dict() for goal in goals])

@financial_goal_bp.route('/<int:id>', methods=['GET'])
def get_goal(id):
    """
    取得單一財務目標
    GET /api/goals/<id>
    """
    goal = FinancialGoal.query.get_or_404(id)
    return jsonify(goal.to_dict())

@financial_goal_bp.route('', methods=['POST'])
def create_goal():
    """
    建立新財務目標
    POST /api/goals
    """
    data = request.get_json()
    
    deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data.get('deadline') else None
    
    goal = FinancialGoal(
        name=data['name'],
        target_amount=data['target_amount'],
        current_amount=data.get('current_amount', 0),
        deadline=deadline,
        priority=data.get('priority', 1),
        description=data.get('description')
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify(goal.to_dict()), 201

@financial_goal_bp.route('/<int:id>', methods=['PUT'])
def update_goal(id):
    """
    更新財務目標
    PUT /api/goals/<id>
    """
    goal = FinancialGoal.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('deadline'):
        goal.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    
    goal.name = data.get('name', goal.name)
    goal.target_amount = data.get('target_amount', goal.target_amount)
    goal.current_amount = data.get('current_amount', goal.current_amount)
    goal.priority = data.get('priority', goal.priority)
    goal.status = data.get('status', goal.status)
    goal.description = data.get('description', goal.description)
    
    # 自動檢查是否達成目標
    if float(goal.current_amount) >= float(goal.target_amount):
        goal.status = 'completed'
    
    db.session.commit()
    
    return jsonify(goal.to_dict())

@financial_goal_bp.route('/<int:id>', methods=['DELETE'])
def delete_goal(id):
    """
    刪除財務目標
    DELETE /api/goals/<id>
    """
    goal = FinancialGoal.query.get_or_404(id)
    
    db.session.delete(goal)
    db.session.commit()
    
    return jsonify({'message': '財務目標已刪除'}), 200

@financial_goal_bp.route('/<int:id>/add-money', methods=['POST'])
def add_money_to_goal(id):
    """
    為目標增加存款金額
    POST /api/goals/<id>/add-money
    """
    goal = FinancialGoal.query.get_or_404(id)
    data = request.get_json()
    
    amount = float(data.get('amount', 0))
    goal.current_amount = float(goal.current_amount) + amount
    
    # 自動檢查是否達成目標
    if float(goal.current_amount) >= float(goal.target_amount):
        goal.status = 'completed'
    
    db.session.commit()
    
    return jsonify(goal.to_dict())