"""
Category API 路由
處理分類的 CRUD 操作
"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.category import Category

# 建立 Blueprint
category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@category_bp.route('', methods=['GET'])
def get_categories():
    """
    取得所有分類
    GET /api/categories
    可選參數: type (income/expense)
    """
    query = Category.query
    
    # 篩選條件
    if request.args.get('type'):
        query = query.filter(Category.type == request.args.get('type'))
    
    categories = query.filter(Category.is_active == True).all()
    
    return jsonify([category.to_dict() for category in categories])

@category_bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    """
    取得單一分類
    GET /api/categories/<id>
    """
    category = Category.query.get_or_404(id)
    return jsonify(category.to_dict())

@category_bp.route('', methods=['POST'])
def create_category():
    """
    建立新分類
    POST /api/categories
    """
    data = request.get_json()
    
    category = Category(
        name=data['name'],
        type=data['type'],
        parent_id=data.get('parent_id'),
        color=data.get('color'),
        icon=data.get('icon'),
        description=data.get('description')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

@category_bp.route('/<int:id>', methods=['PUT'])
def update_category(id):
    """
    更新分類
    PUT /api/categories/<id>
    """
    category = Category.query.get_or_404(id)
    data = request.get_json()
    
    category.name = data.get('name', category.name)
    category.type = data.get('type', category.type)
    category.parent_id = data.get('parent_id', category.parent_id)
    category.color = data.get('color', category.color)
    category.icon = data.get('icon', category.icon)
    category.description = data.get('description', category.description)
    category.is_active = data.get('is_active', category.is_active)
    
    db.session.commit()
    
    return jsonify(category.to_dict())

@category_bp.route('/<int:id>', methods=['DELETE'])
def delete_category(id):
    """
    刪除分類（軟刪除，設為非啟用）
    DELETE /api/categories/<id>
    """
    category = Category.query.get_or_404(id)
    
    # 軟刪除：只是設為非啟用
    category.is_active = False
    db.session.commit()
    
    return jsonify({'message': '分類已刪除'}), 200