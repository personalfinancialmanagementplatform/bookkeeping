"""
投資組合 API 路由
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import text
from datetime import datetime, date
import json

portfolio_bp = Blueprint('portfolio', __name__)

# db 會在 run.py 中設定
db = None

def init_portfolio_routes(database):
    """初始化資料庫連接"""
    global db
    db = database


# ============================================
# 投資帳戶 API
# ============================================

@portfolio_bp.route('/api/investment-accounts', methods=['GET'])
def get_investment_accounts():
    """取得所有投資帳戶"""
    try:
        result = db.session.execute(text('''
            SELECT id, name, account_type, broker, currency, description, is_active, created_at
            FROM investment_accounts
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        '''))
        
        accounts = []
        for row in result:
            accounts.append({
                'id': row[0],
                'name': row[1],
                'account_type': row[2],
                'broker': row[3],
                'currency': row[4],
                'description': row[5],
                'is_active': row[6],
                'created_at': str(row[7]) if row[7] else None
            })
        
        return jsonify(accounts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/investment-accounts', methods=['POST'])
def create_investment_account():
    """建立投資帳戶"""
    try:
        data = request.get_json()
        
        db.session.execute(text('''
            INSERT INTO investment_accounts (name, account_type, broker, currency, description)
            VALUES (:name, :account_type, :broker, :currency, :description)
        '''), {
            'name': data.get('name'),
            'account_type': data.get('account_type', 'general'),
            'broker': data.get('broker'),
            'currency': data.get('currency', 'TWD'),
            'description': data.get('description')
        })
        db.session.commit()
        
        return jsonify({'message': '投資帳戶建立成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 持倉 API
# ============================================

@portfolio_bp.route('/api/holdings', methods=['GET'])
def get_holdings():
    """取得所有持倉"""
    try:
        account_id = request.args.get('account_id')
        
        if account_id:
            result = db.session.execute(text('''
                SELECT h.id, h.account_id, h.symbol, h.name, h.quantity, 
                       h.average_cost, h.asset_type, h.market, h.created_at,
                       ia.name as account_name
                FROM holdings h
                JOIN investment_accounts ia ON h.account_id = ia.id
                WHERE h.quantity > 0 AND h.account_id = :account_id
                ORDER BY h.asset_type, h.symbol
            '''), {'account_id': account_id})
        else:
            result = db.session.execute(text('''
                SELECT h.id, h.account_id, h.symbol, h.name, h.quantity, 
                       h.average_cost, h.asset_type, h.market, h.created_at,
                       ia.name as account_name
                FROM holdings h
                JOIN investment_accounts ia ON h.account_id = ia.id
                WHERE h.quantity > 0
                ORDER BY h.asset_type, h.symbol
            '''))
        
        holdings = []
        for row in result:
            qty = float(row[4]) if row[4] else 0
            cost = float(row[5]) if row[5] else 0
            holdings.append({
                'id': row[0],
                'account_id': row[1],
                'symbol': row[2],
                'name': row[3],
                'quantity': qty,
                'average_cost': cost,
                'asset_type': row[6],
                'market': row[7],
                'created_at': str(row[8]) if row[8] else None,
                'account_name': row[9],
                'total_cost': qty * cost
            })
        
        return jsonify(holdings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/holdings', methods=['POST'])
def create_holding():
    """新增持倉"""
    try:
        data = request.get_json()
        
        # 檢查是否已存在
        result = db.session.execute(text('''
            SELECT id, quantity, average_cost FROM holdings
            WHERE account_id = :account_id AND symbol = :symbol
        '''), {
            'account_id': data.get('account_id'),
            'symbol': data.get('symbol')
        })
        existing = result.fetchone()
        
        if existing:
            # 更新現有持倉（計算新的平均成本）
            old_id, old_qty, old_cost = existing
            new_qty = float(data.get('quantity', 0))
            new_price = float(data.get('price', 0))
            
            total_qty = float(old_qty) + new_qty
            new_avg_cost = ((float(old_qty) * float(old_cost)) + (new_qty * new_price)) / total_qty
            
            db.session.execute(text('''
                UPDATE holdings
                SET quantity = :quantity, average_cost = :avg_cost, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'quantity': total_qty, 'avg_cost': new_avg_cost, 'id': old_id})
            
            holding_id = old_id
        else:
            # 建立新持倉
            result = db.session.execute(text('''
                INSERT INTO holdings (account_id, symbol, name, quantity, average_cost, asset_type, market)
                VALUES (:account_id, :symbol, :name, :quantity, :price, :asset_type, :market)
                RETURNING id
            '''), {
                'account_id': data.get('account_id'),
                'symbol': data.get('symbol'),
                'name': data.get('name'),
                'quantity': data.get('quantity'),
                'price': data.get('price'),
                'asset_type': data.get('asset_type', 'stock'),
                'market': data.get('market', 'TWSE')
            })
            holding_id = result.fetchone()[0]
        
        # 記錄交易
        db.session.execute(text('''
            INSERT INTO investment_transactions 
            (holding_id, transaction_type, quantity, price, fee, tax, transaction_date)
            VALUES (:holding_id, :type, :quantity, :price, :fee, :tax, :date)
        '''), {
            'holding_id': holding_id,
            'type': 'buy',
            'quantity': data.get('quantity'),
            'price': data.get('price'),
            'fee': data.get('fee', 0),
            'tax': data.get('tax', 0),
            'date': data.get('transaction_date', date.today())
        })
        
        db.session.commit()
        return jsonify({'id': holding_id, 'message': '持倉新增成功'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/holdings/<int:holding_id>/sell', methods=['POST'])
def sell_holding(holding_id):
    """賣出持倉"""
    try:
        data = request.get_json()
        sell_qty = float(data.get('quantity', 0))
        sell_price = float(data.get('price', 0))
        
        result = db.session.execute(text(
            'SELECT quantity FROM holdings WHERE id = :id'
        ), {'id': holding_id})
        row = result.fetchone()
        
        if not row:
            return jsonify({'error': '持倉不存在'}), 404
        
        current_qty = float(row[0])
        
        if sell_qty > current_qty:
            return jsonify({'error': '賣出數量超過持有數量'}), 400
        
        new_qty = current_qty - sell_qty
        
        db.session.execute(text('''
            UPDATE holdings SET quantity = :qty, updated_at = CURRENT_TIMESTAMP WHERE id = :id
        '''), {'qty': new_qty, 'id': holding_id})
        
        db.session.execute(text('''
            INSERT INTO investment_transactions 
            (holding_id, transaction_type, quantity, price, fee, tax, transaction_date)
            VALUES (:holding_id, :type, :quantity, :price, :fee, :tax, :date)
        '''), {
            'holding_id': holding_id,
            'type': 'sell',
            'quantity': sell_qty,
            'price': sell_price,
            'fee': data.get('fee', 0),
            'tax': data.get('tax', 0),
            'date': data.get('transaction_date', date.today())
        })
        
        db.session.commit()
        return jsonify({'message': '賣出成功', 'remaining_quantity': new_qty})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 投資組合摘要 API
# ============================================

@portfolio_bp.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """取得投資組合摘要"""
    try:
        from app.services.stock_service import stock_service, PerformanceCalculator
        
        result = db.session.execute(text('''
            SELECT h.id, h.symbol, h.name, h.quantity, h.average_cost, h.asset_type, h.market
            FROM holdings h
            JOIN investment_accounts ia ON h.account_id = ia.id
            WHERE h.quantity > 0 AND ia.is_active = TRUE
        '''))
        
        holdings = []
        for row in result:
            holdings.append({
                'id': row[0],
                'symbol': row[1],
                'name': row[2],
                'quantity': float(row[3]) if row[3] else 0,
                'average_cost': float(row[4]) if row[4] else 0,
                'asset_type': row[5],
                'market': row[6]
            })
        
        total_cost = 0
        total_value = 0
        holdings_with_value = []
        
        # 取得即時股價
        symbols = [h['symbol'] for h in holdings if h['asset_type'] != 'cash']
        prices = {}
        
        if symbols:
            price_data = stock_service.get_realtime_prices(symbols)
            for p in price_data:
                if p.get('success'):
                    prices[p['symbol']] = p['price']
        
        for h in holdings:
            qty = h['quantity']
            cost = h['average_cost']
            
            if h['asset_type'] == 'cash':
                current_price = 1
            else:
                current_price = prices.get(h['symbol'], cost)
            
            market_value = qty * current_price
            cost_basis = qty * cost
            profit = market_value - cost_basis
            profit_rate = PerformanceCalculator.calculate_roi(market_value, cost_basis)
            
            total_cost += cost_basis
            total_value += market_value
            
            holdings_with_value.append({
                **h,
                'current_price': current_price,
                'market_value': round(market_value, 2),
                'cost_basis': round(cost_basis, 2),
                'profit': round(profit, 2),
                'profit_rate': profit_rate
            })
        
        total_profit = total_value - total_cost
        total_profit_rate = PerformanceCalculator.calculate_roi(total_value, total_cost)
        
        # 資產配置
        allocation = {}
        for h in holdings_with_value:
            asset_type = h['asset_type']
            if asset_type not in allocation:
                allocation[asset_type] = {'value': 0, 'count': 0}
            allocation[asset_type]['value'] += h['market_value']
            allocation[asset_type]['count'] += 1
        
        for asset_type in allocation:
            allocation[asset_type]['percentage'] = round(
                allocation[asset_type]['value'] / total_value * 100, 2
            ) if total_value > 0 else 0
        
        return jsonify({
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'total_profit_rate': total_profit_rate,
            'holdings_count': len(holdings_with_value),
            'allocation': allocation,
            'holdings': holdings_with_value,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 關注清單 API
# ============================================

@portfolio_bp.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """取得關注清單"""
    try:
        from app.services.stock_service import stock_service
        
        result = db.session.execute(text('''
            SELECT id, symbol, name, alert_price_high, alert_price_low, alert_change_percent, note
            FROM watchlist ORDER BY created_at DESC
        '''))
        
        watchlist = []
        for row in result:
            watchlist.append({
                'id': row[0],
                'symbol': row[1],
                'name': row[2],
                'alert_price_high': float(row[3]) if row[3] else None,
                'alert_price_low': float(row[4]) if row[4] else None,
                'alert_change_percent': float(row[5]) if row[5] else None,
                'note': row[6]
            })
        
        # 取得即時股價
        if watchlist:
            symbols = [w['symbol'] for w in watchlist]
            prices = stock_service.get_realtime_prices(symbols)
            price_map = {p['symbol']: p for p in prices if p.get('success')}
            
            for w in watchlist:
                if w['symbol'] in price_map:
                    w['current_price'] = price_map[w['symbol']].get('price')
                    w['change'] = price_map[w['symbol']].get('change')
        
        return jsonify(watchlist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """新增到關注清單"""
    try:
        data = request.get_json()
        
        db.session.execute(text('''
            INSERT INTO watchlist (symbol, name, alert_price_high, alert_price_low, note)
            VALUES (:symbol, :name, :high, :low, :note)
        '''), {
            'symbol': data.get('symbol'),
            'name': data.get('name'),
            'high': data.get('alert_price_high'),
            'low': data.get('alert_price_low'),
            'note': data.get('note')
        })
        db.session.commit()
        
        return jsonify({'message': '已加入關注清單'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/watchlist/<int:watchlist_id>', methods=['DELETE'])
def remove_from_watchlist(watchlist_id):
    """從關注清單移除"""
    try:
        db.session.execute(text('DELETE FROM watchlist WHERE id = :id'), {'id': watchlist_id})
        db.session.commit()
        return jsonify({'message': '已從關注清單移除'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 股票搜尋 API
# ============================================

@portfolio_bp.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """搜尋股票"""
    try:
        from app.services.stock_service import stock_service
        
        keyword = request.args.get('q', '')
        limit = int(request.args.get('limit', 20))
        
        if len(keyword) < 1:
            return jsonify([])
        
        results = stock_service.search_stocks(keyword, limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/stocks/quote/<symbol>', methods=['GET'])
def get_stock_quote(symbol):
    """取得即時股價"""
    try:
        from app.services.stock_service import stock_service
        
        quote = stock_service.get_realtime_price(symbol)
        return jsonify(quote)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# 風險評估 API
# ============================================

@portfolio_bp.route('/api/risk-assessment', methods=['POST'])
def create_risk_assessment():
    """進行風險評估"""
    try:
        from app.services.stock_service import RiskAssessment
        
        data = request.get_json()
        
        result = RiskAssessment.calculate_investable_amount(
            monthly_disposable=float(data.get('monthly_disposable', 0)),
            monthly_savings_goal=float(data.get('monthly_savings_goal', 0)),
            risk_profile=data.get('risk_profile', 'balanced'),
            has_emergency_fund=data.get('has_emergency_fund', True),
            has_debt=data.get('has_debt', False)
        )
        
        if result['recommended_amount'] > 0:
            portfolio_rec = RiskAssessment.get_portfolio_recommendation(
                investable_amount=result['recommended_amount'],
                risk_profile=data.get('risk_profile', 'balanced')
            )
            result['portfolio_recommendation'] = portfolio_rec
        
        # 儲存到資料庫
        db.session.execute(text('''
            INSERT INTO risk_assessments 
            (assessment_date, risk_tolerance, investment_horizon, loss_tolerance,
             risk_score, recommended_allocation, monthly_income, monthly_expense,
             has_debt, recommended_investable_amount)
            VALUES (:date, :tolerance, :horizon, :loss, :score, :allocation, 
                    :income, :expense, :debt, :amount)
        '''), {
            'date': date.today(),
            'tolerance': data.get('risk_profile'),
            'horizon': data.get('investment_horizon'),
            'loss': data.get('loss_tolerance'),
            'score': data.get('risk_score'),
            'allocation': json.dumps(result.get('allocation')),
            'income': data.get('monthly_income'),
            'expense': data.get('monthly_expense'),
            'debt': data.get('has_debt', False),
            'amount': result['recommended_amount']
        })
        db.session.commit()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/monthly-stats', methods=['GET'])

def get_portfolio_monthly_stats():
    """取得本月投資統計"""
    try:
        from datetime import datetime, date
        
        # 本月起始日
        start_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        # 本月買入總額
        buy_result = db.session.execute(text('''
            SELECT COALESCE(SUM(quantity * price + fee), 0)
            FROM investment_transactions
            WHERE transaction_type = 'buy' AND transaction_date >= :start
        '''), {'start': start_of_month})
        monthly_investment = float(buy_result.scalar() or 0)
        
        # 本月賣出總額
        sell_result = db.session.execute(text('''
            SELECT COALESCE(SUM(quantity * price - fee), 0)
            FROM investment_transactions
            WHERE transaction_type = 'sell' AND transaction_date >= :start
        '''), {'start': start_of_month})
        monthly_sell = float(sell_result.scalar() or 0)
        
        # 本月股息收入
        dividend_result = db.session.execute(text('''
            SELECT COALESCE(SUM(quantity * price), 0)
            FROM investment_transactions
            WHERE transaction_type = 'dividend' AND transaction_date >= :start
        '''), {'start': start_of_month})
        monthly_dividend = float(dividend_result.scalar() or 0)
        
        # 本月交易次數
        trade_count_result = db.session.execute(text('''
            SELECT COUNT(*)
            FROM investment_transactions
            WHERE transaction_date >= :start
        '''), {'start': start_of_month})
        trade_count = int(trade_count_result.scalar() or 0)
        
        # 最近交易記錄
        recent_result = db.session.execute(text('''
            SELECT it.transaction_type, it.quantity, it.price, it.transaction_date,
                   h.symbol, h.name
            FROM investment_transactions it
            JOIN holdings h ON it.holding_id = h.id
            ORDER BY it.created_at DESC
            LIMIT 5
        '''))
        
        recent_transactions = []
        for row in recent_result:
            recent_transactions.append({
                'type': row[0],
                'quantity': float(row[1]),
                'price': float(row[2]),
                'date': str(row[3]),
                'symbol': row[4],
                'name': row[5],
                'amount': float(row[1]) * float(row[2])
            })
        
        return jsonify({
            'monthly_investment': round(monthly_investment, 0),
            'monthly_sell': round(monthly_sell, 0),
            'monthly_dividend': round(monthly_dividend, 0),
            'monthly_profit': round(monthly_sell + monthly_dividend - monthly_investment, 0),
            'trade_count': trade_count,
            'recent_transactions': recent_transactions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500