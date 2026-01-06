"""
推薦標的資料庫服務
從證交所抓取全部上市股票與 ETF 資料
"""

import requests
import twstock
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import threading
import csv
import io


class RecommendationService:
    """推薦標的資料庫服務 - 完整版"""
    
    # 證交所 API
    TWSE_STOCK_LIST_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/BWIBBU_d"
    TWSE_ETF_LIST_URL = "https://www.twse.com.tw/rwd/zh/ETF/etfDiv"
    
    # 證交所股票清單 CSV
    TWSE_STOCK_CSV = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    TWSE_ETF_CSV = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 86400  # 快取 24 小時
        self._lock = threading.Lock()
        
        # 從 twstock 取得所有股票代碼
        self._all_stocks = twstock.codes
    
    def _fetch_all_stocks_from_twse(self) -> List[Dict]:
        """從證交所抓取全部上市股票"""
        stocks = []
        
        try:
            response = requests.get(self.TWSE_STOCK_CSV, timeout=30)
            response.encoding = 'big5'
            
            lines = response.text.split('\n')
            current_category = ''
            
            for line in lines:
                if '股票' in line and '有價證券' not in line:
                    current_category = '股票'
                elif 'ETF' in line or '指數股票型' in line:
                    current_category = 'ETF'
                
                parts = line.split('　')
                if len(parts) >= 5:
                    try:
                        code_name = parts[0].strip()
                        if '　' in code_name:
                            code, name = code_name.split('　', 1)
                        else:
                            continue
                        
                        code = code.strip()
                        name = name.strip()
                        
                        # 只取數字代碼（排除權證等）
                        if code.isdigit() and len(code) == 4:
                            stocks.append({
                                'symbol': code,
                                'name': name,
                                'type': 'stock',
                                'category': current_category
                            })
                    except:
                        continue
                        
        except Exception as e:
            print(f"從證交所抓取股票清單失敗: {e}")
        
        return stocks
    
    def _fetch_all_etfs_from_twse(self) -> List[Dict]:
        """從證交所抓取全部 ETF"""
        etfs = []
        
        try:
            response = requests.get(self.TWSE_ETF_CSV, timeout=30)
            response.encoding = 'big5'
            
            lines = response.text.split('\n')
            
            for line in lines:
                parts = line.split('　')
                if len(parts) >= 2:
                    try:
                        code_name = parts[0].strip()
                        if '　' in code_name:
                            code, name = code_name.split('　', 1)
                        else:
                            continue
                        
                        code = code.strip()
                        name = name.strip()
                        
                        # ETF 代碼格式：4-6 碼數字或含 B
                        if (code.isdigit() and 4 <= len(code) <= 6) or 'B' in code:
                            etfs.append({
                                'symbol': code,
                                'name': name,
                                'type': 'etf'
                            })
                    except:
                        continue
                        
        except Exception as e:
            print(f"從證交所抓取 ETF 清單失敗: {e}")
        
        return etfs
    
    def get_all_from_twstock(self) -> Dict:
        """從 twstock 取得全部股票與 ETF（最完整）"""
        cache_key = 'all_from_twstock'
        now = datetime.now()
        
        with self._lock:
            if cache_key in self._cache:
                cache_time = self._cache_time.get(cache_key)
                if cache_time and (now - cache_time).seconds < self._cache_duration:
                    return self._cache[cache_key]
        
        all_stocks = []
        all_etfs = []
        
        for code, info in self._all_stocks.items():
            try:
                item = {
                    'symbol': code,
                    'name': info.name,
                    'market': info.market,  # 上市/上櫃
                    'group': info.group,    # 產業分類
                    'start_date': info.start.strftime('%Y-%m-%d') if info.start else None,
                }
                
                # 判斷是否為 ETF
                if info.type == '指數型基金' or 'ETF' in info.name or code.endswith('B'):
                    item['type'] = 'etf'
                    item['category'] = self._categorize_etf(code, info.name)
                    all_etfs.append(item)
                else:
                    item['type'] = 'stock'
                    item['sector'] = info.group
                    item['category'] = self._categorize_stock(info.group)
                    all_stocks.append(item)
                    
            except Exception as e:
                continue
        
        result = {
            'stocks': all_stocks,
            'etfs': all_etfs,
            'stock_count': len(all_stocks),
            'etf_count': len(all_etfs),
            'total_count': len(all_stocks) + len(all_etfs),
            'last_updated': now.isoformat()
        }
        
        with self._lock:
            self._cache[cache_key] = result
            self._cache_time[cache_key] = now
        
        return result
    
    def _categorize_etf(self, symbol: str, name: str) -> str:
        """自動分類 ETF"""
        name_lower = name.lower()
        
        # 債券型
        if 'B' in symbol or '債' in name or 'bond' in name_lower:
            if '美債' in name or '美國' in name:
                return 'us_bond'
            elif '公司債' in name or '投資級' in name:
                return 'corporate_bond'
            else:
                return 'bond'
        
        # 高股息
        if '高股息' in name or '高息' in name:
            if '月配' in name:
                return 'monthly_dividend'
            return 'high_dividend'
        
        # 大盤型
        if '台灣50' in name or '台50' in name or '加權' in name:
            return 'market_cap'
        
        # 產業型
        if '半導體' in name:
            return 'semiconductor'
        if '5G' in name or '通訊' in name:
            return '5g_telecom'
        if '電動車' in name or 'EV' in name:
            return 'ev'
        if 'AI' in name or '人工智慧' in name:
            return 'ai'
        if '金融' in name or '銀行' in name:
            return 'financial'
        if 'ESG' in name or '永續' in name:
            return 'esg'
        
        # 海外型
        if 'S&P' in name or '美國' in name or '美股' in name:
            return 'us_market'
        if 'NASDAQ' in name or '那斯達克' in name:
            return 'nasdaq'
        if '日本' in name or '日經' in name:
            return 'japan'
        if '中國' in name or '陸股' in name:
            return 'china'
        if '全球' in name or '世界' in name:
            return 'global'
        
        # 其他
        if '低波動' in name or '低波' in name:
            return 'low_volatility'
        if '成長' in name:
            return 'growth'
        
        return 'other'
    
    def _categorize_stock(self, group: str) -> str:
        """自動分類股票"""
        if not group:
            return 'other'
        
        group_mapping = {
            '半導體業': 'semiconductor',
            '電腦及週邊設備業': 'computer',
            '光電業': 'optoelectronics',
            '通信網路業': 'telecom',
            '電子零組件業': 'electronics',
            '電子通路業': 'electronics_channel',
            '資訊服務業': 'it_service',
            '其他電子業': 'other_electronics',
            '金融保險業': 'financial',
            '食品工業': 'food',
            '塑膠工業': 'plastic',
            '紡織纖維': 'textile',
            '電機機械': 'machinery',
            '電器電纜': 'electrical',
            '化學工業': 'chemical',
            '生技醫療業': 'biotech',
            '油電燃氣業': 'energy',
            '鋼鐵工業': 'steel',
            '橡膠工業': 'rubber',
            '汽車工業': 'automotive',
            '建材營造業': 'construction',
            '航運業': 'shipping',
            '觀光餐旅業': 'tourism',
            '貿易百貨業': 'retail',
            '其他業': 'other',
        }
        
        return group_mapping.get(group, 'other')
    
    def get_all_etfs(self, category: str = None) -> List[Dict]:
        """取得全部 ETF（可篩選分類）"""
        data = self.get_all_from_twstock()
        etfs = data.get('etfs', [])
        
        if category:
            etfs = [e for e in etfs if e.get('category') == category]
        
        return etfs
    
    def get_all_stocks(self, category: str = None, sector: str = None) -> List[Dict]:
        """取得全部股票（可篩選分類/產業）"""
        data = self.get_all_from_twstock()
        stocks = data.get('stocks', [])
        
        if category:
            stocks = [s for s in stocks if s.get('category') == category]
        
        if sector:
            stocks = [s for s in stocks if s.get('sector') == sector]
        
        return stocks
    
    def get_etf_categories(self) -> Dict[str, int]:
        """取得 ETF 分類統計"""
        data = self.get_all_from_twstock()
        etfs = data.get('etfs', [])
        
        categories = {}
        for etf in etfs:
            cat = etf.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories
    
    def get_stock_sectors(self) -> Dict[str, int]:
        """取得股票產業統計"""
        data = self.get_all_from_twstock()
        stocks = data.get('stocks', [])
        
        sectors = {}
        for stock in stocks:
            sector = stock.get('sector', '其他')
            sectors[sector] = sectors.get(sector, 0) + 1
        
        return sectors
    
    def search(self, keyword: str, limit: int = 50) -> List[Dict]:
        """搜尋全部標的"""
        data = self.get_all_from_twstock()
        results = []
        keyword = keyword.lower()
        
        # 搜尋 ETF
        for etf in data.get('etfs', []):
            if (keyword in etf['symbol'].lower() or 
                keyword in etf['name'].lower()):
                results.append({**etf, 'type': 'ETF'})
        
        # 搜尋股票
        for stock in data.get('stocks', []):
            if (keyword in stock['symbol'].lower() or 
                keyword in stock['name'].lower()):
                results.append({**stock, 'type': '股票'})
        
        return results[:limit]
    
    def get_by_risk_level(self, risk_level: str) -> Dict:
        """根據風險等級取得推薦（使用自動分類）"""
        data = self.get_all_from_twstock()
        
        # 風險等級對應的 ETF 分類
        risk_etf_mapping = {
            'conservative': ['bond', 'us_bond', 'corporate_bond', 'low_volatility'],
            'moderate': ['market_cap', 'high_dividend', 'esg', 'bond', 'us_bond'],
            'aggressive': ['semiconductor', '5g_telecom', 'ev', 'ai', 'nasdaq', 'growth', 'monthly_dividend'],
        }
        
        # 風險等級對應的股票產業
        risk_stock_mapping = {
            'conservative': ['financial', 'food', 'retail'],
            'moderate': ['financial', 'computer', 'electronics', 'telecom'],
            'aggressive': ['semiconductor', 'optoelectronics', 'biotech', 'it_service'],
        }
        
        allowed_etf_cats = risk_etf_mapping.get(risk_level, risk_etf_mapping['moderate'])
        allowed_stock_cats = risk_stock_mapping.get(risk_level, risk_stock_mapping['moderate'])
        
        filtered_etfs = [e for e in data.get('etfs', []) if e.get('category') in allowed_etf_cats]
        filtered_stocks = [s for s in data.get('stocks', []) if s.get('category') in allowed_stock_cats]
        
        return {
            'etfs': filtered_etfs[:30],  # 限制數量
            'stocks': filtered_stocks[:30],
            'risk_level': risk_level,
            'etf_count': len(filtered_etfs),
            'stock_count': len(filtered_stocks)
        }
    
    def get_by_goal(self, goal: str) -> Dict:
        """根據投資目標取得推薦"""
        data = self.get_all_from_twstock()
        
        goal_etf_mapping = {
            'retirement': ['high_dividend', 'monthly_dividend', 'bond', 'us_bond', 'corporate_bond', 'low_volatility'],
            'growth': ['market_cap', 'semiconductor', '5g_telecom', 'ev', 'ai', 'nasdaq', 'growth'],
            'income': ['high_dividend', 'monthly_dividend', 'bond', 'corporate_bond'],
            'preservation': ['bond', 'us_bond', 'corporate_bond', 'low_volatility', 'market_cap'],
        }
        
        goal_stock_mapping = {
            'retirement': ['financial', 'food', 'retail'],
            'growth': ['semiconductor', 'optoelectronics', 'computer', 'it_service'],
            'income': ['financial', 'food', 'energy'],
            'preservation': ['financial', 'food', 'retail', 'energy'],
        }
        
        allowed_etf_cats = goal_etf_mapping.get(goal, goal_etf_mapping['growth'])
        allowed_stock_cats = goal_stock_mapping.get(goal, goal_stock_mapping['growth'])
        
        filtered_etfs = [e for e in data.get('etfs', []) if e.get('category') in allowed_etf_cats]
        filtered_stocks = [s for s in data.get('stocks', []) if s.get('category') in allowed_stock_cats]
        
        return {
            'etfs': filtered_etfs[:30],
            'stocks': filtered_stocks[:30],
            'goal': goal,
            'etf_count': len(filtered_etfs),
            'stock_count': len(filtered_stocks)
        }
    
    def get_statistics(self) -> Dict:
        """取得完整統計"""
        data = self.get_all_from_twstock()
        
        return {
            'total_count': data.get('total_count', 0),
            'stock_count': data.get('stock_count', 0),
            'etf_count': data.get('etf_count', 0),
            'etf_categories': self.get_etf_categories(),
            'stock_sectors': self.get_stock_sectors(),
            'last_updated': data.get('last_updated')
        }
    
    def get_popular(self) -> Dict:
        """取得熱門標的（精選）"""
        return {
            'etf': {
                'market_cap': [
                    {'symbol': '0050', 'name': '元大台灣50', 'highlight': '台股大盤首選'},
                    {'symbol': '006208', 'name': '富邦台50', 'highlight': '費用率最低'},
                ],
                'high_dividend': [
                    {'symbol': '0056', 'name': '元大高股息', 'highlight': '高股息元老'},
                    {'symbol': '00878', 'name': '國泰永續高股息', 'highlight': 'ESG+高股息'},
                    {'symbol': '00713', 'name': '元大台灣高息低波', 'highlight': '低波動策略'},
                ],
                'monthly_dividend': [
                    {'symbol': '00919', 'name': '群益台灣精選高息', 'highlight': '月配息人氣王'},
                    {'symbol': '00929', 'name': '復華台灣科技優息', 'highlight': '科技+月配'},
                    {'symbol': '00939', 'name': '統一台灣高息動能', 'highlight': '動能策略'},
                    {'symbol': '00940', 'name': '元大台灣價值高息', 'highlight': '價值投資'},
                ],
                'bond': [
                    {'symbol': '00679B', 'name': '元大美債20年', 'highlight': '美國公債'},
                    {'symbol': '00720B', 'name': '元大投資級公司債', 'highlight': '投資級債券'},
                ],
            },
            'stock': {
                'growth': [
                    {'symbol': '2330', 'name': '台積電', 'highlight': '護國神山'},
                    {'symbol': '2454', 'name': '聯發科', 'highlight': 'IC設計龍頭'},
                    {'symbol': '2382', 'name': '廣達', 'highlight': 'AI伺服器'},
                ],
                'financial': [
                    {'symbol': '2881', 'name': '富邦金', 'highlight': '金控獲利王'},
                    {'symbol': '2882', 'name': '國泰金', 'highlight': '壽險龍頭'},
                    {'symbol': '2886', 'name': '兆豐金', 'highlight': '官股金控'},
                ],
                'defensive': [
                    {'symbol': '2412', 'name': '中華電', 'highlight': '電信龍頭'},
                    {'symbol': '1216', 'name': '統一', 'highlight': '食品龍頭'},
                ],
            }
        }


# 建立服務實例
recommendation_service = RecommendationService()