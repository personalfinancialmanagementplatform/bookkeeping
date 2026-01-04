"""
台股數據服務 (增強版)
使用 twstock 套件取得台灣股市數據

功能：
1. 台股即時報價 (twstock - TWSE/TPEX)
2. 美股即時報價 (Yahoo Finance API)
3. 30秒快取機制避免 API 限流
4. 批次查詢多檔股票
5. 股票搜尋功能
6. 投資績效計算
7. 風險評估與配置建議
8. 非交易時間顯示收盤價
"""

import ssl
import os

# 修復 SSL 憑證問題
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

# 讓 requests 也忽略 SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
old_request = requests.Session.request
def new_request(self, *args, **kwargs):
    kwargs['verify'] = False
    return old_request(self, *args, **kwargs)
requests.Session.request = new_request

import twstock
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import time


# ============================================
# 快取系統
# ============================================
class StockCache:
    """
    股價快取系統
    - 避免頻繁請求被封鎖
    - TWSE 限制：每 5 秒 3 個 request
    """
    
    def __init__(self, ttl_seconds: int = 30):
        self._cache: Dict[str, Dict] = {}
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
    
    def get(self, symbol: str) -> Optional[Dict]:
        """從快取取得資料"""
        with self._lock:
            if symbol in self._cache:
                entry = self._cache[symbol]
                if datetime.now() - entry['timestamp'] < timedelta(seconds=self._ttl):
                    return entry['data']
            return None
    
    def set(self, symbol: str, data: Dict):
        """存入快取"""
        with self._lock:
            self._cache[symbol] = {
                'data': data,
                'timestamp': datetime.now()
            }
    
    def clear(self, symbol: str = None):
        """清除快取"""
        with self._lock:
            if symbol:
                self._cache.pop(symbol, None)
            else:
                self._cache.clear()


# ============================================
# 股票服務主類別 (增強版)
# ============================================
class StockService:
    """
    台股數據服務類 (增強版)
    - 台股：twstock (TWSE/TPEX)
    - 美股：Yahoo Finance API
    - 快取機制
    - 限流機制
    - 非交易時間顯示收盤價
    """
    
    def __init__(self):
        """初始化服務"""
        self.cache = StockCache(ttl_seconds=30)
        self._rate_limit_lock = threading.Lock()
        self._last_request_time = {}
        
        try:
            twstock.__update_codes()
        except:
            pass
    
    def _rate_limit(self, source: str, min_interval: float = 1.0):
        """
        限流機制
        - TWSE 限制：每 5 秒 3 個 request → 約 1.7 秒一個
        """
        with self._rate_limit_lock:
            now = time.time()
            last = self._last_request_time.get(source, 0)
            if now - last < min_interval:
                time.sleep(min_interval - (now - last))
            self._last_request_time[source] = time.time()
    
    def _is_tw_stock(self, symbol: str) -> bool:
        """判斷是否為台股"""
        return symbol.isdigit() or symbol in twstock.codes
    
    def _parse_price(self, value) -> float:
        """解析價格字串"""
        if value is None or value == '-' or value == '':
            return 0.0
        try:
            return float(str(value).replace(',', ''))
        except:
            return 0.0
    
    # ==========================================
    # 主要 API：取得即時股價
    # ==========================================
    def get_realtime_price(self, symbol: str) -> Dict[str, Any]:
        """取得即時股價，非交易時間返回最近收盤價"""
        # 檢查快取
        cached = self.cache.get(symbol)
        if cached:
            return cached
        
        try:
            # 判斷是否為台股
            if self._is_tw_stock(symbol):
                result = self._get_tw_stock_price(symbol)
            else:
                result = self._get_us_stock_price(symbol)
            
            # 如果成功，存入快取
            if result.get('success'):
                self.cache.set(symbol, result)
            
            return result
            
        except Exception as e:
            print(f"取得股價失敗 {symbol}: {e}")
            return {'success': False, 'symbol': symbol, 'error': str(e)}
    
    # ==========================================
    # 台股股價（即時 + 收盤價備援）
    # ==========================================
    def _get_tw_stock_price(self, symbol: str) -> Dict[str, Any]:
        """取得台股股價（即時 + 收盤價備援）"""
        try:
            # 限流
            self._rate_limit('TWSE', 1.7)
            
            # 方法 1: 嘗試即時報價
            stock = twstock.realtime.get(symbol)
            
            if stock and stock.get('success'):
                realtime = stock.get('realtime', {})
                info = stock.get('info', {})
                
                price = self._parse_price(realtime.get('latest_trade_price'))
                
                if price > 0:
                    yesterday_close = self._parse_price(info.get('lastDayClose'))
                    change = price - yesterday_close if yesterday_close else 0
                    change_percent = (change / yesterday_close * 100) if yesterday_close else 0
                    
                    stock_info = twstock.codes.get(symbol)
                    name = stock_info.name if stock_info else info.get('name', symbol)
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'name': name,
                        'price': price,
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'high': self._parse_price(realtime.get('high')),
                        'low': self._parse_price(realtime.get('low')),
                        'open': self._parse_price(realtime.get('open')),
                        'volume': int(realtime.get('accumulate_trade_volume', 0) or 0),
                        'timestamp': realtime.get('latest_trade_time', ''),
                        'source': 'realtime',
                        'note': '即時報價'
                    }
            
            # 方法 2: 即時報價失敗或為 0，取得歷史收盤價
            return self._get_tw_closing_price(symbol)
            
        except Exception as e:
            print(f"台股即時報價失敗 {symbol}: {e}")
            # 嘗試取得收盤價
            return self._get_tw_closing_price(symbol)
    
    def _get_tw_closing_price(self, symbol: str) -> Dict[str, Any]:
        """取得台股最近收盤價"""
        try:
            # 使用 twstock.Stock 取得歷史資料
            stock = twstock.Stock(symbol)
            
            if stock.price and len(stock.price) > 0:
                # 取得最近一天的收盤價
                latest_price = stock.price[-1]
                latest_date = stock.date[-1] if stock.date else None
                
                # 計算漲跌
                change = 0
                change_percent = 0
                if len(stock.price) >= 2:
                    prev_price = stock.price[-2]
                    change = latest_price - prev_price
                    change_percent = (change / prev_price * 100) if prev_price > 0 else 0
                
                # 取得股票名稱
                stock_info = twstock.codes.get(symbol)
                name = stock_info.name if stock_info else symbol
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'name': name,
                    'price': float(latest_price),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'source': 'closing',
                    'date': latest_date.strftime('%Y-%m-%d') if latest_date else None,
                    'note': '收盤價（非交易時間）'
                }
            
            # 方法 3: 如果 twstock 都失敗，用 Yahoo Finance
            return self._get_tw_stock_from_yahoo(symbol)
            
        except Exception as e:
            print(f"取得收盤價失敗 {symbol}: {e}")
            return self._get_tw_stock_from_yahoo(symbol)
    
    def _get_tw_stock_from_yahoo(self, symbol: str) -> Dict[str, Any]:
        """從 Yahoo Finance 取得台股報價（備援方案）"""
        try:
            # 台股在 Yahoo Finance 的格式是 symbol.TW 或 symbol.TWO (上櫃)
            yahoo_symbol = f"{symbol}.TW"
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            data = response.json()
            
            result = data.get('chart', {}).get('result', [])
            if result:
                meta = result[0].get('meta', {})
                price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('previousClose', 0)
                
                if price and price > 0:
                    change = price - prev_close if prev_close else 0
                    change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'name': meta.get('shortName', symbol),
                        'price': float(price),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'source': 'yahoo',
                        'note': '資料來源: Yahoo Finance'
                    }
            
            # 嘗試上櫃股票 (.TWO)
            yahoo_symbol = f"{symbol}.TWO"
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            data = response.json()
            
            result = data.get('chart', {}).get('result', [])
            if result:
                meta = result[0].get('meta', {})
                price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('previousClose', 0)
                
                if price and price > 0:
                    change = price - prev_close if prev_close else 0
                    change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'name': meta.get('shortName', symbol),
                        'price': float(price),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'source': 'yahoo',
                        'note': '資料來源: Yahoo Finance'
                    }
            
            return {'success': False, 'symbol': symbol, 'error': '無法取得股價'}
            
        except Exception as e:
            print(f"Yahoo Finance 取得失敗 {symbol}: {e}")
            return {'success': False, 'symbol': symbol, 'error': str(e)}
    
    # ==========================================
    # 美股即時報價
    # ==========================================
    def _get_us_stock_price(self, symbol: str) -> Dict[str, Any]:
        """取得美股即時報價 (Yahoo Finance)"""
        try:
            self._rate_limit('YAHOO', 0.5)
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'interval': '1d', 'range': '1d'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                return {
                    'symbol': symbol,
                    'success': False,
                    'error': '無法取得資料'
                }
            
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', 0)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return {
                'symbol': symbol,
                'name': meta.get('shortName', symbol),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'high': round(meta.get('regularMarketDayHigh', 0), 2),
                'low': round(meta.get('regularMarketDayLow', 0), 2),
                'open': round(meta.get('regularMarketOpen', 0), 2),
                'close': round(previous_close, 2),
                'volume': meta.get('regularMarketVolume', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': meta.get('currency', 'USD'),
                'source': 'yahoo',
                'success': True
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'success': False,
                'error': str(e)
            }
    
    # ==========================================
    # 批次查詢 (增強版)
    # ==========================================
    def get_batch_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        批次取得多檔股票即時報價
        
        Args:
            symbols: ['2330', '2317', '0050', 'AAPL']
        
        Returns:
            {
                '2330': {'symbol': '2330', 'price': 1050, ...},
                '2317': {'symbol': '2317', 'price': 180, ...}
            }
        """
        results = {}
        
        # 分離台股和美股
        tw_symbols = [s for s in symbols if self._is_tw_stock(s)]
        us_symbols = [s for s in symbols if not self._is_tw_stock(s)]
        
        # 台股逐一查詢（使用新的備援機制）
        for symbol in tw_symbols:
            results[symbol] = self.get_realtime_price(symbol)
        
        # 美股逐一查詢
        for symbol in us_symbols:
            results[symbol] = self.get_realtime_price(symbol)
        
        return results
    
    def _process_tw_realtime(self, symbol: str, data: Dict) -> Dict:
        """處理 twstock 回傳資料"""
        if not data or not data.get('success'):
            # 嘗試取得收盤價
            return self._get_tw_closing_price(symbol)
        
        info = data.get('info', {})
        realtime = data.get('realtime', {})
        
        latest_price = self._parse_price(realtime.get('latest_trade_price'))
        
        # 如果即時價格為 0，取得收盤價
        if latest_price <= 0:
            return self._get_tw_closing_price(symbol)
        
        yesterday_close = self._parse_price(info.get('lastDayClose'))
        change = latest_price - yesterday_close if yesterday_close else 0
        change_percent = (change / yesterday_close * 100) if yesterday_close else 0
        
        stock_info = twstock.codes.get(symbol)
        name = stock_info.name if stock_info else info.get('name', symbol)
        
        return {
            'symbol': symbol,
            'name': name,
            'price': latest_price,
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'high': self._parse_price(realtime.get('high')),
            'low': self._parse_price(realtime.get('low')),
            'open': self._parse_price(realtime.get('open')),
            'volume': int(realtime.get('accumulate_trade_volume', 0) or 0),
            'timestamp': realtime.get('latest_trade_time', ''),
            'source': 'TWSE' if info.get('exchange') == 'TAI' else 'TPEX',
            'success': True
        }
    
    # ==========================================
    # 舊版相容方法
    # ==========================================
    def get_realtime_prices(self, symbols: List[str]) -> List[Dict]:
        """批量取得即時股價（舊版相容）"""
        batch_results = self.get_batch_prices(symbols)
        return [batch_results.get(s, {'symbol': s, 'success': False}) for s in symbols]
    
    # ==========================================
    # 股票搜尋
    # ==========================================
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜尋股票"""
        results = []
        try:
            for code, info in twstock.codes.items():
                if keyword.upper() in code or keyword in info.name:
                    results.append({
                        'symbol': code,
                        'name': info.name,
                        'type': info.type,
                        'market': info.market,
                        'industry': info.group
                    })
                    if len(results) >= limit:
                        break
            return results
        except:
            return []
    
    # ==========================================
    # 股票基本資訊
    # ==========================================
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """取得股票基本資訊"""
        try:
            if symbol in twstock.codes:
                info = twstock.codes[symbol]
                return {
                    'symbol': symbol,
                    'name': info.name,
                    'type': info.type,
                    'market': info.market,
                    'group': info.group,
                    'industry': info.group,
                    'start_date': info.start,
                    'success': True
                }
            return {'symbol': symbol, 'success': False, 'error': '找不到股票資訊'}
        except:
            return {'symbol': symbol, 'success': False, 'error': '查詢失敗'}
    
    # ==========================================
    # 歷史資料
    # ==========================================
    def get_historical_data(self, symbol: str, months: int = 3) -> List[Dict]:
        """
        取得歷史股價資料
        
        Args:
            symbol: 股票代碼
            months: 取得幾個月的資料
        """
        try:
            stock = twstock.Stock(symbol)
            
            now = datetime.now()
            start_year = now.year
            start_month = now.month - months
            if start_month <= 0:
                start_year -= 1
                start_month += 12
            
            stock.fetch_from(start_year, start_month)
            
            return [
                {
                    'date': d.date.strftime('%Y-%m-%d'),
                    'open': d.open,
                    'high': d.high,
                    'low': d.low,
                    'close': d.close,
                    'volume': d.capacity,
                    'change': d.change
                }
                for d in stock.data
            ]
        except Exception as e:
            return []


# ============================================
# 投資績效計算器
# ============================================
class PerformanceCalculator:
    """投資績效計算器"""
    
    @staticmethod
    def calculate_roi(current_value: float, cost: float) -> float:
        """計算投資報酬率 (ROI)"""
        if cost == 0:
            return 0
        return round((current_value - cost) / cost * 100, 2)
    
    @staticmethod
    def calculate_annualized_return(current_value: float, cost: float, holding_days: int) -> float:
        """計算年化報酬率"""
        if cost == 0 or holding_days == 0:
            return 0
        total_return = current_value / cost
        annualized = (total_return ** (365 / holding_days)) - 1
        return round(annualized * 100, 2)


# ============================================
# 風險評估
# ============================================
class RiskAssessment:
    """風險評估"""
    
    RISK_FACTORS = {
        'conservative': {'k': 0.25, 'label': '保守型'},
        'balanced': {'k': 0.5, 'label': '穩健型'},
        'aggressive': {'k': 0.75, 'label': '積極型'}
    }
    
    ALLOCATION_TEMPLATES = {
        'conservative': {'stock': 15, 'etf': 35, 'bond': 35, 'fund': 10, 'cash': 5},
        'balanced': {'stock': 35, 'etf': 45, 'bond': 10, 'fund': 5, 'cash': 5},
        'aggressive': {'stock': 60, 'etf': 30, 'bond': 5, 'fund': 3, 'cash': 2}
    }
    
    @classmethod
    def calculate_investable_amount(cls, monthly_disposable: float, monthly_savings_goal: float,
                                     risk_profile: str, has_emergency_fund: bool = True,
                                     has_debt: bool = False) -> Dict:
        """計算建議可投資金額"""
        warnings = []
        
        if not has_emergency_fund:
            warnings.append('建議先建立3-6個月的緊急預備金再開始投資')
        if has_debt:
            warnings.append('建議優先償還高利率負債')
        
        available = monthly_disposable - monthly_savings_goal
        
        if available <= 0:
            return {
                'recommended_amount': 0,
                'risk_profile': risk_profile,
                'warnings': warnings + ['每月可支配金額不足以同時儲蓄和投資'],
                'allocation': None
            }
        
        factor_info = cls.RISK_FACTORS.get(risk_profile, cls.RISK_FACTORS['balanced'])
        k = factor_info['k']
        
        if has_debt or not has_emergency_fund:
            k = k * 0.5
        
        recommended = round(available * k, 0)
        
        return {
            'recommended_amount': recommended,
            'available_after_savings': available,
            'risk_profile': risk_profile,
            'risk_profile_label': factor_info['label'],
            'risk_factor': k,
            'warnings': warnings,
            'allocation': cls.ALLOCATION_TEMPLATES.get(risk_profile)
        }
    
    @classmethod
    def get_portfolio_recommendation(cls, investable_amount: float, risk_profile: str) -> Dict:
        """取得投資組合配置建議"""
        allocation = cls.ALLOCATION_TEMPLATES.get(risk_profile, cls.ALLOCATION_TEMPLATES['balanced'])
        
        portfolio = {}
        for asset_type, percentage in allocation.items():
            amount = round(investable_amount * percentage / 100, 0)
            portfolio[asset_type] = {'percentage': percentage, 'amount': amount}
        
        etf_recommendations = [
            {'symbol': '0050', 'name': '元大台灣50', 'type': '大盤型'},
            {'symbol': '006208', 'name': '富邦台50', 'type': '大盤型'},
            {'symbol': '0056', 'name': '元大高股息', 'type': '高股息'},
            {'symbol': '00878', 'name': '國泰永續高股息', 'type': '高股息ESG'},
        ]
        
        return {
            'investable_amount': investable_amount,
            'risk_profile': risk_profile,
            'allocation': portfolio,
            'etf_recommendations': etf_recommendations,
            'notes': [
                '建議以定期定額方式投入，降低進場時機風險',
                '投資組合應定期檢視，必要時進行再平衡',
                '以上為參考建議，實際投資請依個人情況調整'
            ]
        }


# ============================================
# 建立服務實例
# ============================================
stock_service = StockService()
performance_calculator = PerformanceCalculator()
risk_assessment = RiskAssessment()