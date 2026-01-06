"""
推薦標的資料庫服務
從證交所、投信網站抓取 ETF/股票資料
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import json


class RecommendationService:
    """推薦標的資料庫服務"""
    
    # 證交所 API
    TWSE_ETF_URL = "https://www.twse.com.tw/rwd/zh/ETF/etfDiv"
    TWSE_STOCK_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d"
    
    # 基本資料 API
    TWSE_INFO_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY"
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 86400  # 快取 24 小時
        self._lock = threading.Lock()
        
        # 預設推薦標的（基礎資料）
        self._default_recommendations = self._init_default_recommendations()
    
    def _init_default_recommendations(self) -> Dict:
        """初始化預設推薦標的"""
        return {
            'etf': {
                'market_cap': [
                    {'symbol': '0050', 'name': '元大台灣50', 'category': '大盤型', 'risk_level': 'RR4', 'expense_ratio': 0.32, 'dividend_yield': 3.5},
                    {'symbol': '006208', 'name': '富邦台50', 'category': '大盤型', 'risk_level': 'RR4', 'expense_ratio': 0.15, 'dividend_yield': 3.3},
                ],
                'high_dividend': [
                    {'symbol': '0056', 'name': '元大高股息', 'category': '高股息', 'risk_level': 'RR4', 'expense_ratio': 0.66, 'dividend_yield': 6.5},
                    {'symbol': '00878', 'name': '國泰永續高股息', 'category': '高股息', 'risk_level': 'RR4', 'expense_ratio': 0.25, 'dividend_yield': 7.0},
                    {'symbol': '00713', 'name': '元大台灣高息低波', 'category': '低波動高股息', 'risk_level': 'RR3', 'expense_ratio': 0.35, 'dividend_yield': 6.0},
                ],
                'monthly_dividend': [
                    {'symbol': '00919', 'name': '群益台灣精選高息', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 8.0},
                    {'symbol': '00929', 'name': '復華台灣科技優息', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 7.5},
                    {'symbol': '00934', 'name': '中信成長高股息', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 7.0},
                    {'symbol': '00936', 'name': '台新臺灣永續高息', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 7.2},
                    {'symbol': '00939', 'name': '統一台灣高息動能', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 6.8},
                    {'symbol': '00940', 'name': '元大台灣價值高息', 'category': '月配息', 'risk_level': 'RR4', 'expense_ratio': 0.35, 'dividend_yield': 6.5},
                ],
                'bond': [
                    {'symbol': '00679B', 'name': '元大美債20年', 'category': '美國公債', 'risk_level': 'RR2', 'expense_ratio': 0.10, 'dividend_yield': 4.5},
                    {'symbol': '00687B', 'name': '國泰20年美債', 'category': '美國公債', 'risk_level': 'RR2', 'expense_ratio': 0.10, 'dividend_yield': 4.3},
                    {'symbol': '00720B', 'name': '元大投資級公司債', 'category': '投資級債券', 'risk_level': 'RR2', 'expense_ratio': 0.30, 'dividend_yield': 5.0},
                    {'symbol': '00751B', 'name': '元大AAA至A公司債', 'category': '投資級債券', 'risk_level': 'RR2', 'expense_ratio': 0.25, 'dividend_yield': 4.8},
                    {'symbol': '00772B', 'name': '中信高評級公司債', 'category': '投資級債券', 'risk_level': 'RR2', 'expense_ratio': 0.28, 'dividend_yield': 4.6},
                ],
                'sector': [
                    {'symbol': '00881', 'name': '國泰台灣5G+', 'category': '5G通訊', 'risk_level': 'RR4', 'expense_ratio': 0.40, 'dividend_yield': 3.0},
                    {'symbol': '00891', 'name': '中信關鍵半導體', 'category': '半導體', 'risk_level': 'RR5', 'expense_ratio': 0.40, 'dividend_yield': 2.5},
                    {'symbol': '00892', 'name': '富邦台灣半導體', 'category': '半導體', 'risk_level': 'RR5', 'expense_ratio': 0.40, 'dividend_yield': 2.3},
                    {'symbol': '00893', 'name': '國泰智能電動車', 'category': '電動車', 'risk_level': 'RR5', 'expense_ratio': 0.60, 'dividend_yield': 1.5},
                ],
                'global': [
                    {'symbol': '00646', 'name': '元大S&P500', 'category': '美股大盤', 'risk_level': 'RR4', 'expense_ratio': 0.50, 'dividend_yield': 1.5},
                    {'symbol': '00662', 'name': '富邦NASDAQ', 'category': '美股科技', 'risk_level': 'RR5', 'expense_ratio': 0.50, 'dividend_yield': 0.8},
                    {'symbol': '00830', 'name': '國泰費城半導體', 'category': '美股半導體', 'risk_level': 'RR5', 'expense_ratio': 0.55, 'dividend_yield': 0.5},
                ],
            },
            'stock': {
                'growth': [
                    {'symbol': '2330', 'name': '台積電', 'category': '成長型', 'sector': '半導體', 'risk_level': 'RR4', 'dividend_yield': 1.8},
                    {'symbol': '2454', 'name': '聯發科', 'category': '成長型', 'sector': '半導體', 'risk_level': 'RR5', 'dividend_yield': 3.5},
                    {'symbol': '2382', 'name': '廣達', 'category': '成長型', 'sector': 'AI伺服器', 'risk_level': 'RR4', 'dividend_yield': 3.0},
                    {'symbol': '3443', 'name': '創意', 'category': '成長型', 'sector': 'IC設計', 'risk_level': 'RR5', 'dividend_yield': 2.0},
                    {'symbol': '2379', 'name': '瑞昱', 'category': '成長型', 'sector': 'IC設計', 'risk_level': 'RR4', 'dividend_yield': 4.0},
                ],
                'stable': [
                    {'symbol': '2317', 'name': '鴻海', 'category': '穩健型', 'sector': '電子代工', 'risk_level': 'RR3', 'dividend_yield': 5.0},
                    {'symbol': '2881', 'name': '富邦金', 'category': '穩健型', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 5.5},
                    {'symbol': '2882', 'name': '國泰金', 'category': '穩健型', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 5.0},
                    {'symbol': '2884', 'name': '玉山金', 'category': '穩健型', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 4.5},
                    {'symbol': '2886', 'name': '兆豐金', 'category': '穩健型', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 5.2},
                    {'symbol': '2891', 'name': '中信金', 'category': '穩健型', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 5.8},
                ],
                'defensive': [
                    {'symbol': '1216', 'name': '統一', 'category': '防禦型', 'sector': '食品', 'risk_level': 'RR2', 'dividend_yield': 4.0},
                    {'symbol': '1301', 'name': '台塑', 'category': '防禦型', 'sector': '塑化', 'risk_level': 'RR3', 'dividend_yield': 5.5},
                    {'symbol': '1303', 'name': '南亞', 'category': '防禦型', 'sector': '塑化', 'risk_level': 'RR3', 'dividend_yield': 5.0},
                    {'symbol': '2412', 'name': '中華電', 'category': '防禦型', 'sector': '電信', 'risk_level': 'RR2', 'dividend_yield': 4.5},
                    {'symbol': '9910', 'name': '豐泰', 'category': '防禦型', 'sector': '製鞋', 'risk_level': 'RR3', 'dividend_yield': 4.0},
                ],
                'high_dividend': [
                    {'symbol': '2888', 'name': '新光金', 'category': '高股息', 'sector': '金融', 'risk_level': 'RR3', 'dividend_yield': 6.0},
                    {'symbol': '5880', 'name': '合庫金', 'category': '高股息', 'sector': '金融', 'risk_level': 'RR2', 'dividend_yield': 5.5},
                    {'symbol': '2834', 'name': '臺企銀', 'category': '高股息', 'sector': '金融', 'risk_level': 'RR2', 'dividend_yield': 5.8},
                    {'symbol': '2838', 'name': '聯邦銀', 'category': '高股息', 'sector': '金融', 'risk_level': 'RR2', 'dividend_yield': 5.5},
                ],
            }
        }
    
    def _fetch_etf_info(self, symbol: str) -> Optional[Dict]:
        """從網路抓取 ETF 資訊"""
        try:
            # 嘗試從證交所抓取
            url = f"https://www.twse.com.tw/rwd/zh/ETF/etfInfo?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('stat') == 'OK' and data.get('data'):
                    return self._parse_etf_data(data['data'][0], symbol)
        except Exception as e:
            print(f"抓取 ETF {symbol} 資訊失敗: {e}")
        
        return None
    
    def _fetch_stock_dividend(self, symbol: str) -> Optional[float]:
        """抓取股票殖利率"""
        try:
            url = f"https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d?stockNo={symbol}&response=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('stat') == 'OK' and data.get('data'):
                    # 取最新一筆殖利率
                    latest = data['data'][-1]
                    try:
                        yield_rate = float(latest[2]) if latest[2] != '--' else 0
                        return yield_rate
                    except:
                        pass
        except Exception as e:
            print(f"抓取股票 {symbol} 殖利率失敗: {e}")
        
        return None
    
    def _fetch_current_price(self, symbol: str) -> Optional[float]:
        """抓取當前股價"""
        try:
            import twstock
            stock = twstock.realtime.get(symbol)
            if stock and stock.get('success'):
                return float(stock['realtime']['latest_trade_price'])
        except Exception as e:
            print(f"抓取 {symbol} 股價失敗: {e}")
        
        return None
    
    def get_all_recommendations(self) -> Dict:
        """取得所有推薦標的（含即時資料更新）"""
        cache_key = 'all_recommendations'
        now = datetime.now()
        
        with self._lock:
            if cache_key in self._cache:
                cache_time = self._cache_time.get(cache_key)
                if cache_time and (now - cache_time).seconds < self._cache_duration:
                    return self._cache[cache_key]
        
        # 使用預設資料，並嘗試更新即時資訊
        recommendations = self._default_recommendations.copy()
        
        # 更新部分即時資料（避免太多 API 請求）
        try:
            # 只更新熱門標的的股價
            hot_symbols = ['0050', '0056', '00878', '2330', '2317']
            for symbol in hot_symbols:
                price = self._fetch_current_price(symbol)
                if price:
                    self._update_price_in_recommendations(recommendations, symbol, price)
        except Exception as e:
            print(f"更新即時資料失敗: {e}")
        
        with self._lock:
            self._cache[cache_key] = recommendations
            self._cache_time[cache_key] = now
        
        return recommendations
    
    def _update_price_in_recommendations(self, recommendations: Dict, symbol: str, price: float):
        """更新推薦標的中的股價"""
        for asset_type in recommendations.values():
            for category in asset_type.values():
                for item in category:
                    if item['symbol'] == symbol:
                        item['current_price'] = price
    
    def get_etf_list(self, category: str = None) -> List[Dict]:
        """取得 ETF 清單"""
        recommendations = self.get_all_recommendations()
        etf_data = recommendations.get('etf', {})
        
        if category:
            return etf_data.get(category, [])
        
        # 合併所有 ETF
        all_etfs = []
        for etfs in etf_data.values():
            all_etfs.extend(etfs)
        
        return all_etfs
    
    def get_stock_list(self, category: str = None) -> List[Dict]:
        """取得股票清單"""
        recommendations = self.get_all_recommendations()
        stock_data = recommendations.get('stock', {})
        
        if category:
            return stock_data.get(category, [])
        
        # 合併所有股票
        all_stocks = []
        for stocks in stock_data.values():
            all_stocks.extend(stocks)
        
        return all_stocks
    
    def get_by_risk_level(self, risk_level: str) -> Dict:
        """根據風險等級取得推薦標的"""
        recommendations = self.get_all_recommendations()
        
        risk_mapping = {
            'conservative': ['RR1', 'RR2'],
            'moderate': ['RR1', 'RR2', 'RR3'],
            'aggressive': ['RR1', 'RR2', 'RR3', 'RR4', 'RR5'],
        }
        
        allowed_risks = risk_mapping.get(risk_level, ['RR1', 'RR2', 'RR3'])
        
        filtered = {'etf': [], 'stock': []}
        
        # 篩選 ETF
        for category, etfs in recommendations.get('etf', {}).items():
            for etf in etfs:
                if etf.get('risk_level') in allowed_risks:
                    filtered['etf'].append(etf)
        
        # 篩選股票
        for category, stocks in recommendations.get('stock', {}).items():
            for stock in stocks:
                if stock.get('risk_level') in allowed_risks:
                    filtered['stock'].append(stock)
        
        return filtered
    
    def get_by_goal(self, goal: str) -> Dict:
        """根據投資目標取得推薦標的"""
        recommendations = self.get_all_recommendations()
        
        goal_mapping = {
            'retirement': {
                'etf_categories': ['high_dividend', 'bond', 'market_cap'],
                'stock_categories': ['stable', 'defensive', 'high_dividend']
            },
            'growth': {
                'etf_categories': ['market_cap', 'sector', 'global'],
                'stock_categories': ['growth', 'stable']
            },
            'income': {
                'etf_categories': ['high_dividend', 'monthly_dividend', 'bond'],
                'stock_categories': ['high_dividend', 'stable']
            },
            'preservation': {
                'etf_categories': ['bond', 'market_cap'],
                'stock_categories': ['defensive', 'stable']
            }
        }
        
        goal_config = goal_mapping.get(goal, goal_mapping['growth'])
        
        filtered = {'etf': [], 'stock': []}
        
        # 篩選 ETF
        for category in goal_config['etf_categories']:
            etfs = recommendations.get('etf', {}).get(category, [])
            filtered['etf'].extend(etfs)
        
        # 篩選股票
        for category in goal_config['stock_categories']:
            stocks = recommendations.get('stock', {}).get(category, [])
            filtered['stock'].extend(stocks)
        
        # 去除重複
        seen_etf = set()
        unique_etfs = []
        for etf in filtered['etf']:
            if etf['symbol'] not in seen_etf:
                seen_etf.add(etf['symbol'])
                unique_etfs.append(etf)
        filtered['etf'] = unique_etfs
        
        seen_stock = set()
        unique_stocks = []
        for stock in filtered['stock']:
            if stock['symbol'] not in seen_stock:
                seen_stock.add(stock['symbol'])
                unique_stocks.append(stock)
        filtered['stock'] = unique_stocks
        
        return filtered
    
    def search(self, keyword: str) -> List[Dict]:
        """搜尋推薦標的"""
        recommendations = self.get_all_recommendations()
        results = []
        keyword = keyword.lower()
        
        # 搜尋 ETF
        for category, etfs in recommendations.get('etf', {}).items():
            for etf in etfs:
                if (keyword in etf['symbol'].lower() or 
                    keyword in etf['name'].lower() or
                    keyword in etf.get('category', '').lower()):
                    results.append({**etf, 'type': 'ETF'})
        
        # 搜尋股票
        for category, stocks in recommendations.get('stock', {}).items():
            for stock in stocks:
                if (keyword in stock['symbol'].lower() or 
                    keyword in stock['name'].lower() or
                    keyword in stock.get('sector', '').lower()):
                    results.append({**stock, 'type': '股票'})
        
        return results
    
    def get_statistics(self) -> Dict:
        """取得推薦標的統計"""
        recommendations = self.get_all_recommendations()
        
        etf_count = sum(len(etfs) for etfs in recommendations.get('etf', {}).values())
        stock_count = sum(len(stocks) for stocks in recommendations.get('stock', {}).values())
        
        return {
            'total': etf_count + stock_count,
            'etf_count': etf_count,
            'stock_count': stock_count,
            'etf_categories': list(recommendations.get('etf', {}).keys()),
            'stock_categories': list(recommendations.get('stock', {}).keys()),
            'last_updated': datetime.now().isoformat()
        }


# 建立服務實例
recommendation_service = RecommendationService()