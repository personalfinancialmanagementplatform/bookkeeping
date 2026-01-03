"""
台股數據服務
使用 twstock 套件取得台灣股市數據
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
from datetime import datetime
from typing import Dict, List, Optional


class StockService:
    """台股數據服務類"""
    
    def __init__(self):
        """初始化服務"""
        try:
            twstock.__update_codes()
        except:
            pass
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict]:
        """取得即時股價"""
        try:
            data = twstock.realtime.get(symbol)
            
            if data['success']:
                realtime = data['realtime']
                info = data['info']
                
                return {
                    'symbol': symbol,
                    'name': info.get('name', ''),
                    'price': float(realtime.get('latest_trade_price', 0) or 0),
                    'change': float(realtime.get('change', 0) or 0),
                    'volume': int(realtime.get('accumulate_trade_volume', 0) or 0),
                    'high': float(realtime.get('high', 0) or 0),
                    'low': float(realtime.get('low', 0) or 0),
                    'open': float(realtime.get('open', 0) or 0),
                    'time': info.get('time', ''),
                    'success': True
                }
            return {'symbol': symbol, 'success': False, 'error': '無法取得數據'}
        except Exception as e:
            return {'symbol': symbol, 'success': False, 'error': str(e)}
    
    def get_realtime_prices(self, symbols: List[str]) -> List[Dict]:
        """批量取得即時股價"""
        try:
            data = twstock.realtime.get(symbols)
            results = []
            
            for symbol in symbols:
                if symbol in data and data[symbol]['success']:
                    realtime = data[symbol]['realtime']
                    info = data[symbol]['info']
                    
                    results.append({
                        'symbol': symbol,
                        'name': info.get('name', ''),
                        'price': float(realtime.get('latest_trade_price', 0) or 0),
                        'change': float(realtime.get('change', 0) or 0),
                        'volume': int(realtime.get('accumulate_trade_volume', 0) or 0),
                        'success': True
                    })
                else:
                    results.append({'symbol': symbol, 'success': False})
            
            return results
        except Exception as e:
            return [{'symbol': s, 'success': False, 'error': str(e)} for s in symbols]
    
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
                    'start_date': info.start
                }
            return None
        except:
            return None
    
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
                        'market': info.market
                    })
                    if len(results) >= limit:
                        break
            return results
        except:
            return []


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


# 建立服務實例
stock_service = StockService()
performance_calculator = PerformanceCalculator()
risk_assessment = RiskAssessment()