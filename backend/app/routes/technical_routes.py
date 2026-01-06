"""
技術指標 API 路由
提供 KD、MA 等技術指標分析和訊號偵測
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

technical_bp = Blueprint('technical', __name__)

# db 會在 run.py 中設定
db = None

def init_technical_routes(database):
    """初始化資料庫連接"""
    global db
    db = database


@technical_bp.route('/api/technical/signals', methods=['GET'])
def get_portfolio_signals():
    """取得投資組合的技術訊號"""
    try:
        from app.services.technical_indicator_service import technical_indicator_service
        from sqlalchemy import text
        
        # 取得所有持倉
        result = db.session.execute(text('''
            SELECT h.symbol, h.name, h.asset_type
            FROM holdings h
            JOIN investment_accounts ia ON h.account_id = ia.id
            WHERE h.quantity > 0 AND ia.is_active = TRUE
        '''))
        
        holdings = []
        for row in result:
            # 只分析股票和 ETF（台股）
            if row[2] in ['stock', 'etf'] and row[0].isdigit():
                holdings.append({
                    'symbol': row[0],
                    'name': row[1],
                    'asset_type': row[2]
                })
        
        if not holdings:
            return jsonify({
                'signals': [],
                'summary': {
                    'total_analyzed': 0,
                    'buy_signals': 0,
                    'sell_signals': 0,
                    'total_signals': 0
                },
                'message': '沒有可分析的持倉',
                'updated_at': datetime.now().isoformat()
            })
        
        # 分析技術指標
        analysis = technical_indicator_service.analyze_portfolio(holdings)
        
        return jsonify(analysis)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@technical_bp.route('/api/technical/analyze/<symbol>', methods=['GET'])
def analyze_single_stock(symbol):
    """分析單一股票的技術指標"""
    try:
        from app.services.technical_indicator_service import technical_indicator_service
        
        analysis = technical_indicator_service.analyze_stock(symbol)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@technical_bp.route('/api/technical/indicators/<symbol>', methods=['GET'])
def get_stock_indicators(symbol):
    """取得股票當前技術指標數值"""
    try:
        from app.services.technical_indicator_service import technical_indicator_service
        
        indicators = technical_indicator_service.get_stock_indicators(symbol)
        return jsonify(indicators)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@technical_bp.route('/api/technical/batch-analyze', methods=['POST'])
def batch_analyze_stocks():
    """批次分析多檔股票"""
    try:
        from app.services.technical_indicator_service import technical_indicator_service
        
        data = request.get_json() or {}
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': '請提供股票代碼列表'}), 400
        
        if len(symbols) > 20:
            return jsonify({'error': '一次最多分析 20 檔股票'}), 400
        
        results = {}
        for symbol in symbols:
            try:
                analysis = technical_indicator_service.analyze_stock(symbol)
                results[symbol] = analysis
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify({
            'results': results,
            'updated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@technical_bp.route('/api/technical/watchlist-signals', methods=['GET'])
def get_watchlist_signals():
    """取得關注清單的技術訊號"""
    try:
        from app.services.technical_indicator_service import technical_indicator_service
        from sqlalchemy import text
        
        # 取得關注清單
        result = db.session.execute(text('''
            SELECT symbol, name FROM watchlist
        '''))
        
        watchlist = []
        for row in result:
            if row[0].isdigit():  # 只分析台股
                watchlist.append({
                    'symbol': row[0],
                    'name': row[1]
                })
        
        if not watchlist:
            return jsonify({
                'signals': [],
                'summary': {
                    'total_analyzed': 0,
                    'buy_signals': 0,
                    'sell_signals': 0
                },
                'message': '關注清單為空'
            })
        
        analysis = technical_indicator_service.analyze_portfolio(watchlist)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@technical_bp.route('/api/technical/health', methods=['GET'])
def technical_health_check():
    """API 健康檢查"""
    return jsonify({
        'status': 'ok',
        'service': 'technical_indicator_service',
        'timestamp': datetime.now().isoformat()
    })