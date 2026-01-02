"""
Routes 模組
匯出所有 API 路由
"""

from app.routes.account_routes import account_bp
from app.routes.category_routes import category_bp
from app.routes.transaction_routes import transaction_bp
from app.routes.budget_routes import budget_bp
from app.routes.financial_goal_routes import financial_goal_bp

__all__ = ['account_bp', 'category_bp', 'transaction_bp', 'budget_bp', 'financial_goal_bp']