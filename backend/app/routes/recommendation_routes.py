"""
推薦標的 API 路由
"""

from flask import Blueprint, request, jsonify

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/api/recommendations', methods=['GET'])
def get_all_recommendations():
    """取得所有推薦標的"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        recommendations = recommendation_service.get_all_recommendations()
        stats = recommendation_service.get_statistics()
        
        return jsonify({
            'recommendations': recommendations,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/etf', methods=['GET'])
def get_etf_list():
    """取得 ETF 清單"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        category = request.args.get('category')
        etfs = recommendation_service.get_etf_list(category)
        
        return jsonify({
            'etfs': etfs,
            'count': len(etfs),
            'category': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/stock', methods=['GET'])
def get_stock_list():
    """取得股票清單"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        category = request.args.get('category')
        stocks = recommendation_service.get_stock_list(category)
        
        return jsonify({
            'stocks': stocks,
            'count': len(stocks),
            'category': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/by-risk', methods=['GET'])
def get_by_risk_level():
    """根據風險等級取得推薦"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        risk_level = request.args.get('level', 'moderate')
        recommendations = recommendation_service.get_by_risk_level(risk_level)
        
        return jsonify({
            'risk_level': risk_level,
            'recommendations': recommendations,
            'etf_count': len(recommendations['etf']),
            'stock_count': len(recommendations['stock'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/by-goal', methods=['GET'])
def get_by_goal():
    """根據投資目標取得推薦"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        goal = request.args.get('goal', 'growth')
        recommendations = recommendation_service.get_by_goal(goal)
        
        return jsonify({
            'goal': goal,
            'recommendations': recommendations,
            'etf_count': len(recommendations['etf']),
            'stock_count': len(recommendations['stock'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/search', methods=['GET'])
def search_recommendations():
    """搜尋推薦標的"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        keyword = request.args.get('q', '')
        if len(keyword) < 1:
            return jsonify({'error': '請輸入搜尋關鍵字'}), 400
        
        results = recommendation_service.search(keyword)
        
        return jsonify({
            'keyword': keyword,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/statistics', methods=['GET'])
def get_statistics():
    """取得推薦標的統計"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        stats = recommendation_service.get_statistics()
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/categories', methods=['GET'])
def get_categories():
    """取得所有分類"""
    return jsonify({
        'etf_categories': [
            {'key': 'market_cap', 'name': '大盤型', 'description': '追蹤大盤指數，分散投資'},
            {'key': 'high_dividend', 'name': '高股息', 'description': '追求穩定股息收入'},
            {'key': 'monthly_dividend', 'name': '月配息', 'description': '每月配息，現金流穩定'},
            {'key': 'bond', 'name': '債券型', 'description': '固定收益，風險較低'},
            {'key': 'sector', 'name': '產業型', 'description': '聚焦特定產業'},
            {'key': 'global', 'name': '海外型', 'description': '投資海外市場'},
        ],
        'stock_categories': [
            {'key': 'growth', 'name': '成長型', 'description': '高成長潛力股'},
            {'key': 'stable', 'name': '穩健型', 'description': '穩定獲利的藍籌股'},
            {'key': 'defensive', 'name': '防禦型', 'description': '景氣循環影響小'},
            {'key': 'high_dividend', 'name': '高股息', 'description': '高現金股利配發'},
        ]
    })