"""
技術指標服務
計算 KD 指標和移動平均線交叉訊號

KD 指標交叉 (隨機指標):
- 黃金交叉：K線從下方往上穿過D線，是買入訊號
- 死亡交叉：K線從上方往下跌破D線，是賣出訊號
- 超賣區 (<20) 的黃金交叉更可靠
- 超買區 (>80) 的死亡交叉訊號更強

移動平均線 (MA) 交叉:
- 黃金交叉：短期MA向上穿過長期MA，是看漲訊號
- 死亡交叉：短期MA向下穿過長期MA，是看跌訊號
"""

import twstock
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class SignalType(Enum):
    GOLDEN_CROSS = "golden_cross"  # 黃金交叉 - 買入訊號
    DEATH_CROSS = "death_cross"    # 死亡交叉 - 賣出訊號
    NONE = "none"                  # 無訊號


class SignalStrength(Enum):
    STRONG = "strong"      # 強訊號（超買/超賣區）
    NORMAL = "normal"      # 一般訊號
    WEAK = "weak"          # 弱訊號


@dataclass
class TechnicalSignal:
    """技術訊號資料結構"""
    symbol: str
    name: str
    indicator_type: str  # 'KD' or 'MA'
    signal_type: str     # 'golden_cross', 'death_cross', 'none'
    signal_strength: str # 'strong', 'normal', 'weak'
    signal_date: str
    description: str
    recommendation: str  # '買入', '賣出', '觀望'
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class TechnicalIndicatorService:
    """技術指標服務"""
    
    # KD 參數（標準 9-3-3）
    KD_PERIOD = 9       # RSV 計算週期
    K_SMOOTH = 3        # K 值平滑週期
    D_SMOOTH = 3        # D 值平滑週期
    
    # MA 參數
    MA_SHORT = 5        # 短期均線 (5日)
    MA_LONG = 20        # 長期均線 (20日)
    
    # 超買超賣閾值
    OVERBOUGHT = 80     # 超買區
    OVERSOLD = 20       # 超賣區
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 300  # 快取 5 分鐘
        self._lock = threading.Lock()
    
    def _get_stock_history(self, symbol: str, months: int = 3) -> Optional[List[Dict]]:
        """取得股票歷史資料"""
        cache_key = f"history_{symbol}_{months}"
        now = datetime.now()
        
        # 檢查快取
        with self._lock:
            if cache_key in self._cache:
                cache_time = self._cache_time.get(cache_key)
                if cache_time and (now - cache_time).seconds < self._cache_duration:
                    return self._cache[cache_key]
        
        try:
            stock = twstock.Stock(symbol)
            
            # 計算起始月份
            start_year = now.year
            start_month = now.month - months
            if start_month <= 0:
                start_year -= 1
                start_month += 12
            
            # 取得歷史資料
            stock.fetch_from(start_year, start_month)
            
            if not stock.data or len(stock.data) < 20:
                return None
            
            history = []
            for d in stock.data:
                if d.close and d.high and d.low:
                    history.append({
                        'date': d.date,
                        'open': float(d.open) if d.open else 0,
                        'high': float(d.high),
                        'low': float(d.low),
                        'close': float(d.close),
                        'volume': int(d.capacity) if d.capacity else 0
                    })
            
            # 存入快取
            with self._lock:
                self._cache[cache_key] = history
                self._cache_time[cache_key] = now
            
            return history
            
        except Exception as e:
            print(f"取得歷史資料失敗 {symbol}: {e}")
            return None
    
    def _calculate_kd(self, history: List[Dict]) -> Dict[str, List[float]]:
        """
        計算 KD 指標
        RSV = (今日收盤價 - 最近N日最低價) / (最近N日最高價 - 最近N日最低價) × 100
        K = 2/3 × 前日K + 1/3 × 今日RSV
        D = 2/3 × 前日D + 1/3 × 今日K
        """
        if len(history) < self.KD_PERIOD:
            return {'k': [], 'd': [], 'rsv': []}
        
        rsv_list = []
        k_list = []
        d_list = []
        
        # 初始化 K, D 為 50
        prev_k = 50.0
        prev_d = 50.0
        
        for i in range(len(history)):
            if i < self.KD_PERIOD - 1:
                rsv_list.append(50.0)
                k_list.append(50.0)
                d_list.append(50.0)
                continue
            
            # 計算最近 N 日的最高價和最低價
            period_data = history[i - self.KD_PERIOD + 1:i + 1]
            highest = max(d['high'] for d in period_data)
            lowest = min(d['low'] for d in period_data)
            close = history[i]['close']
            
            # 計算 RSV
            if highest == lowest:
                rsv = 50.0
            else:
                rsv = (close - lowest) / (highest - lowest) * 100
            
            # 計算 K 值（平滑）
            k = (2/3) * prev_k + (1/3) * rsv
            
            # 計算 D 值（平滑）
            d = (2/3) * prev_d + (1/3) * k
            
            rsv_list.append(round(rsv, 2))
            k_list.append(round(k, 2))
            d_list.append(round(d, 2))
            
            prev_k = k
            prev_d = d
        
        return {'k': k_list, 'd': d_list, 'rsv': rsv_list}
    
    def _calculate_ma(self, history: List[Dict], period: int) -> List[float]:
        """計算移動平均線"""
        ma_list = []
        
        for i in range(len(history)):
            if i < period - 1:
                ma_list.append(None)
                continue
            
            period_data = history[i - period + 1:i + 1]
            ma = sum(d['close'] for d in period_data) / period
            ma_list.append(round(ma, 2))
        
        return ma_list
    
    def _detect_kd_cross(self, kd_data: Dict, history: List[Dict]) -> Optional[Dict]:
        """
        偵測 KD 交叉訊號
        黃金交叉：K 從下往上穿過 D
        死亡交叉：K 從上往下穿破 D
        """
        k_list = kd_data['k']
        d_list = kd_data['d']
        
        if len(k_list) < 3:
            return None
        
        today_k = k_list[-1]
        today_d = d_list[-1]
        yesterday_k = k_list[-2]
        yesterday_d = d_list[-2]
        
        signal_type = SignalType.NONE
        signal_strength = SignalStrength.NORMAL
        
        # 檢測黃金交叉
        if yesterday_k <= yesterday_d and today_k > today_d:
            signal_type = SignalType.GOLDEN_CROSS
            # 如果在超賣區（<20）發生，訊號更強
            if yesterday_k < self.OVERSOLD or today_k < self.OVERSOLD + 10:
                signal_strength = SignalStrength.STRONG
        
        # 檢測死亡交叉
        elif yesterday_k >= yesterday_d and today_k < today_d:
            signal_type = SignalType.DEATH_CROSS
            # 如果在超買區（>80）發生，訊號更強
            if yesterday_k > self.OVERBOUGHT or today_k > self.OVERBOUGHT - 10:
                signal_strength = SignalStrength.STRONG
        
        if signal_type == SignalType.NONE:
            return None
        
        # 判斷當前狀態
        zone = "中性區"
        if today_k > self.OVERBOUGHT:
            zone = "超買區"
        elif today_k < self.OVERSOLD:
            zone = "超賣區"
        
        return {
            'signal_type': signal_type.value,
            'signal_strength': signal_strength.value,
            'k': today_k,
            'd': today_d,
            'prev_k': yesterday_k,
            'prev_d': yesterday_d,
            'zone': zone,
            'date': history[-1]['date'].strftime('%Y-%m-%d') if history else None
        }
    
    def _detect_ma_cross(self, history: List[Dict]) -> Optional[Dict]:
        """
        偵測均線交叉訊號
        黃金交叉：短期均線從下往上穿過長期均線
        死亡交叉：短期均線從上往下穿破長期均線
        """
        ma_short = self._calculate_ma(history, self.MA_SHORT)
        ma_long = self._calculate_ma(history, self.MA_LONG)
        
        # 需要足夠的資料
        if len(ma_short) < 3 or ma_short[-1] is None or ma_long[-1] is None:
            return None
        
        today_short = ma_short[-1]
        today_long = ma_long[-1]
        yesterday_short = ma_short[-2]
        yesterday_long = ma_long[-2]
        
        if yesterday_short is None or yesterday_long is None:
            return None
        
        signal_type = SignalType.NONE
        signal_strength = SignalStrength.NORMAL
        
        # 檢測黃金交叉
        if yesterday_short <= yesterday_long and today_short > today_long:
            signal_type = SignalType.GOLDEN_CROSS
            # 計算交叉強度（差距百分比）
            diff_pct = abs(today_short - today_long) / today_long * 100
            if diff_pct > 1:
                signal_strength = SignalStrength.STRONG
        
        # 檢測死亡交叉
        elif yesterday_short >= yesterday_long and today_short < today_long:
            signal_type = SignalType.DEATH_CROSS
            diff_pct = abs(today_short - today_long) / today_long * 100
            if diff_pct > 1:
                signal_strength = SignalStrength.STRONG
        
        if signal_type == SignalType.NONE:
            return None
        
        return {
            'signal_type': signal_type.value,
            'signal_strength': signal_strength.value,
            'ma_short': today_short,
            'ma_long': today_long,
            'prev_ma_short': yesterday_short,
            'prev_ma_long': yesterday_long,
            'short_period': self.MA_SHORT,
            'long_period': self.MA_LONG,
            'date': history[-1]['date'].strftime('%Y-%m-%d') if history else None
        }
    
    def analyze_stock(self, symbol: str, name: str = None) -> Dict[str, Any]:
        """分析單一股票的技術指標"""
        # 取得股票名稱
        if not name:
            stock_info = twstock.codes.get(symbol)
            name = stock_info.name if stock_info else symbol
        
        result = {
            'symbol': symbol,
            'name': name,
            'signals': [],
            'current_indicators': {},
            'updated_at': datetime.now().isoformat()
        }
        
        # 取得歷史資料
        history = self._get_stock_history(symbol)
        if not history or len(history) < 20:
            result['error'] = '歷史資料不足'
            return result
        
        # 計算 KD 指標
        kd_data = self._calculate_kd(history)
        
        if kd_data['k']:
            result['current_indicators']['kd'] = {
                'k': kd_data['k'][-1],
                'd': kd_data['d'][-1],
                'zone': '超買區' if kd_data['k'][-1] > 80 else ('超賣區' if kd_data['k'][-1] < 20 else '中性區')
            }
            
            # 偵測 KD 交叉
            kd_signal = self._detect_kd_cross(kd_data, history)
            if kd_signal:
                signal_info = self._format_kd_signal(symbol, name, kd_signal)
                result['signals'].append(signal_info)
        
        # 計算 MA 指標
        ma_short = self._calculate_ma(history, self.MA_SHORT)
        ma_long = self._calculate_ma(history, self.MA_LONG)
        
        if ma_short[-1] and ma_long[-1]:
            result['current_indicators']['ma'] = {
                f'ma{self.MA_SHORT}': ma_short[-1],
                f'ma{self.MA_LONG}': ma_long[-1],
                'trend': '多頭排列' if ma_short[-1] > ma_long[-1] else '空頭排列'
            }
            
            # 偵測 MA 交叉
            ma_signal = self._detect_ma_cross(history)
            if ma_signal:
                signal_info = self._format_ma_signal(symbol, name, ma_signal)
                result['signals'].append(signal_info)
        
        return result
    
    def _format_kd_signal(self, symbol: str, name: str, signal_data: Dict) -> Dict:
        """格式化 KD 訊號"""
        is_golden = signal_data['signal_type'] == 'golden_cross'
        is_strong = signal_data['signal_strength'] == 'strong'
        
        if is_golden:
            recommendation = '買入'
            desc = f"KD指標出現黃金交叉（K值從{signal_data['prev_k']:.1f}上穿D值{signal_data['prev_d']:.1f}）"
            if is_strong:
                desc += f"，且位於{signal_data['zone']}，訊號較強"
        else:
            recommendation = '賣出'
            desc = f"KD指標出現死亡交叉（K值從{signal_data['prev_k']:.1f}下穿D值{signal_data['prev_d']:.1f}）"
            if is_strong:
                desc += f"，且位於{signal_data['zone']}，訊號較強"
        
        return {
            'indicator': 'KD',
            'signal_type': signal_data['signal_type'],
            'signal_strength': signal_data['signal_strength'],
            'recommendation': recommendation,
            'description': desc,
            'details': {
                'k': signal_data['k'],
                'd': signal_data['d'],
                'zone': signal_data['zone'],
                'date': signal_data['date']
            }
        }
    
    def _format_ma_signal(self, symbol: str, name: str, signal_data: Dict) -> Dict:
        """格式化 MA 訊號"""
        is_golden = signal_data['signal_type'] == 'golden_cross'
        is_strong = signal_data['signal_strength'] == 'strong'
        
        short_p = signal_data['short_period']
        long_p = signal_data['long_period']
        
        if is_golden:
            recommendation = '買入'
            desc = f"{short_p}日均線上穿{long_p}日均線，形成黃金交叉"
            if is_strong:
                desc += "，突破幅度明顯"
        else:
            recommendation = '賣出'
            desc = f"{short_p}日均線下穿{long_p}日均線，形成死亡交叉"
            if is_strong:
                desc += "，跌破幅度明顯"
        
        return {
            'indicator': 'MA',
            'signal_type': signal_data['signal_type'],
            'signal_strength': signal_data['signal_strength'],
            'recommendation': recommendation,
            'description': desc,
            'details': {
                f'ma{short_p}': signal_data['ma_short'],
                f'ma{long_p}': signal_data['ma_long'],
                'short_period': short_p,
                'long_period': long_p,
                'date': signal_data['date']
            }
        }
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict[str, Any]:
        """分析投資組合中所有持倉的技術指標"""
        all_signals = []
        buy_count = 0
        sell_count = 0
        
        for holding in holdings:
            symbol = holding.get('symbol')
            name = holding.get('name')
            
            if not symbol:
                continue
            
            # 只分析台股
            if not symbol.isdigit():
                continue
            
            try:
                analysis = self.analyze_stock(symbol, name)
                
                for signal in analysis.get('signals', []):
                    signal['symbol'] = symbol
                    signal['name'] = name
                    signal['current_indicators'] = analysis.get('current_indicators', {})
                    all_signals.append(signal)
                    
                    if signal['recommendation'] == '買入':
                        buy_count += 1
                    elif signal['recommendation'] == '賣出':
                        sell_count += 1
                        
            except Exception as e:
                print(f"分析 {symbol} 失敗: {e}")
                continue
        
        # 排序：強訊號優先，賣出訊號優先（風險提醒）
        all_signals.sort(key=lambda x: (
            0 if x['signal_strength'] == 'strong' else 1,
            0 if x['recommendation'] == '賣出' else 1
        ))
        
        return {
            'signals': all_signals,
            'summary': {
                'total_analyzed': len(holdings),
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'total_signals': len(all_signals)
            },
            'updated_at': datetime.now().isoformat()
        }
    
    def get_stock_indicators(self, symbol: str) -> Dict[str, Any]:
        """取得股票當前技術指標數值（不含訊號判斷）"""
        history = self._get_stock_history(symbol)
        
        if not history or len(history) < 20:
            return {'error': '資料不足'}
        
        # KD
        kd_data = self._calculate_kd(history)
        
        # MA
        ma5 = self._calculate_ma(history, 5)
        ma10 = self._calculate_ma(history, 10)
        ma20 = self._calculate_ma(history, 20)
        ma60 = self._calculate_ma(history, 60) if len(history) >= 60 else [None]
        
        return {
            'symbol': symbol,
            'kd': {
                'k': kd_data['k'][-1] if kd_data['k'] else None,
                'd': kd_data['d'][-1] if kd_data['d'] else None,
                'rsv': kd_data['rsv'][-1] if kd_data['rsv'] else None
            },
            'ma': {
                'ma5': ma5[-1],
                'ma10': ma10[-1],
                'ma20': ma20[-1],
                'ma60': ma60[-1] if ma60 else None
            },
            'price': history[-1]['close'],
            'date': history[-1]['date'].strftime('%Y-%m-%d'),
            'updated_at': datetime.now().isoformat()
        }


# 建立服務實例
technical_indicator_service = TechnicalIndicatorService()