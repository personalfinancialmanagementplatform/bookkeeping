"""
推薦標的 API 路由 - 完整版
"""

from flask import Blueprint, request, jsonify

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/api/recommendations', methods=['GET'])
def get_all_recommendations():
    """取得所有推薦標的（全部上市股票 & ETF）"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        data = recommendation_service.get_all_from_twstock()
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/etf', methods=['GET'])
def get_etf_list():
    """取得全部 ETF（可篩選分類）"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        category = request.args.get('category')
        limit = request.args.get('limit', type=int, default=100)
        
        etfs = recommendation_service.get_all_etfs(category)
        
        return jsonify({
            'etfs': etfs[:limit],
            'total_count': len(etfs),
            'category': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/stock', methods=['GET'])
def get_stock_list():
    """取得全部股票（可篩選產業）"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        category = request.args.get('category')
        sector = request.args.get('sector')
        limit = request.args.get('limit', type=int, default=100)
        
        stocks = recommendation_service.get_all_stocks(category, sector)
        
        return jsonify({
            'stocks': stocks[:limit],
            'total_count': len(stocks),
            'category': category,
            'sector': sector
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/etf/categories', methods=['GET'])
def get_etf_categories():
    """取得 ETF 分類統計"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        categories = recommendation_service.get_etf_categories()
        
        # 分類名稱對照
        category_names = {
            'market_cap': '大盤型',
            'high_dividend': '高股息',
            'monthly_dividend': '月配息',
            'bond': '債券型',
            'us_bond': '美國公債',
            'corporate_bond': '公司債',
            'semiconductor': '半導體',
            '5g_telecom': '5G通訊',
            'ev': '電動車',
            'ai': 'AI人工智慧',
            'financial': '金融',
            'esg': 'ESG永續',
            'us_market': '美股',
            'nasdaq': 'NASDAQ',
            'japan': '日本',
            'china': '中國',
            'global': '全球',
            'low_volatility': '低波動',
            'growth': '成長型',
            'other': '其他',
        }
        
        result = []
        for key, count in sorted(categories.items(), key=lambda x: -x[1]):
            result.append({
                'key': key,
                'name': category_names.get(key, key),
                'count': count
            })
        
        return jsonify({
            'categories': result,
            'total_categories': len(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/stock/sectors', methods=['GET'])
def get_stock_sectors():
    """取得股票產業統計"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        sectors = recommendation_service.get_stock_sectors()
        
        result = []
        for sector, count in sorted(sectors.items(), key=lambda x: -x[1]):
            result.append({
                'sector': sector,
                'count': count
            })
        
        return jsonify({
            'sectors': result,
            'total_sectors': len(result)
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
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/by-goal', methods=['GET'])
def get_by_goal():
    """根據投資目標取得推薦"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        goal = request.args.get('goal', 'growth')
        recommendations = recommendation_service.get_by_goal(goal)
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/search', methods=['GET'])
def search_recommendations():
    """搜尋全部標的"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        keyword = request.args.get('q', '')
        limit = request.args.get('limit', type=int, default=50)
        
        if len(keyword) < 1:
            return jsonify({'error': '請輸入搜尋關鍵字'}), 400
        
        results = recommendation_service.search(keyword, limit)
        
        return jsonify({
            'keyword': keyword,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/popular', methods=['GET'])
def get_popular():
    """取得熱門/精選標的"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        popular = recommendation_service.get_popular()
        
        return jsonify(popular)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendation_bp.route('/api/recommendations/statistics', methods=['GET'])
def get_statistics():
    """取得完整統計"""
    try:
        from app.services.recommendation_service import recommendation_service
        
        stats = recommendation_service.get_statistics()
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500