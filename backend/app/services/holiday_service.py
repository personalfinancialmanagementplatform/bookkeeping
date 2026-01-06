"""
台灣股市休市日服務
從證交所網站抓取休市日資料
"""

import requests
from datetime import datetime, timedelta
from typing import List, Set
import threading


class HolidayService:
    """台灣股市休市日服務"""
    
    # 證交所休市日 API
    TWSE_HOLIDAY_URL = "https://www.twse.com.tw/rwd/zh/holidaySchedule/holidaySchedule"
    
    def __init__(self):
        self._holidays: Set[str] = set()
        self._last_fetch: datetime = None
        self._cache_duration = 86400  # 快取 24 小時
        self._lock = threading.Lock()
    
    def _fetch_holidays(self, year: int = None) -> List[str]:
        """從證交所抓取休市日"""
        if year is None:
            year = datetime.now().year
        
        try:
            # 證交所 API
            response = requests.get(
                self.TWSE_HOLIDAY_URL,
                params={'response': 'json', 'year': year},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                holidays = []
                
                # 解析證交所回傳的資料
                if 'data' in data:
                    for item in data['data']:
                        # 格式: ["114/01/01", "星期三", "中華民國開國紀念日"]
                        # 民國年轉西元年
                        if len(item) >= 1:
                            date_str = item[0]
                            try:
                                parts = date_str.split('/')
                                if len(parts) == 3:
                                    roc_year = int(parts[0])
                                    month = int(parts[1])
                                    day = int(parts[2])
                                    western_year = roc_year + 1911
                                    holidays.append(f"{western_year}-{month:02d}-{day:02d}")
                            except:
                                continue
                
                return holidays
            
        except Exception as e:
            print(f"抓取休市日失敗: {e}")
        
        # 如果抓取失敗，回傳基本假日
        return self._get_default_holidays(year)
    
    def _get_default_holidays(self, year: int) -> List[str]:
        """預設假日（當 API 無法使用時的備案）"""
        # 固定假日
        holidays = [
            f"{year}-01-01",  # 元旦
            f"{year}-02-28",  # 和平紀念日
            f"{year}-04-04",  # 兒童節
            f"{year}-05-01",  # 勞動節
            f"{year}-10-10",  # 國慶日
        ]
        
        # 2025-2027 農曆假日（手動設定）
        lunar_holidays = {
            2025: [
                "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31",  # 春節
                "2025-04-03", "2025-04-04",  # 清明
                "2025-05-30", "2025-05-31",  # 端午
                "2025-10-06", "2025-10-07",  # 中秋
            ],
            2026: [
                "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",  # 春節
                "2026-04-03",  # 清明
                "2026-06-18", "2026-06-19",  # 端午
                "2026-09-24", "2026-09-25",  # 中秋
            ],
            2027: [
                "2027-02-05", "2027-02-06", "2027-02-07", "2027-02-08", "2027-02-09",  # 春節
                "2027-04-05",  # 清明
                "2027-06-08", "2027-06-09",  # 端午
                "2027-10-14", "2027-10-15",  # 中秋
            ],
        }
        
        if year in lunar_holidays:
            holidays.extend(lunar_holidays[year])
        
        return holidays
    
    def get_holidays(self, year: int = None) -> Set[str]:
        """取得休市日集合（含快取）"""
        now = datetime.now()
        
        if year is None:
            year = now.year
        
        with self._lock:
            # 檢查快取
            if self._last_fetch and (now - self._last_fetch).seconds < self._cache_duration:
                return self._holidays
            
            # 抓取當年和明年的假日
            holidays = set()
            for y in [year, year + 1]:
                holidays.update(self._fetch_holidays(y))
            
            self._holidays = holidays
            self._last_fetch = now
            
            return self._holidays
    
    def is_holiday(self, date_str: str) -> bool:
        """檢查是否為休市日"""
        holidays = self.get_holidays()
        return date_str in holidays
    
    def calculate_settlement_date(self, sell_date: str) -> dict:
        """
        計算交割日（T+2 營業日）
        
        Args:
            sell_date: 賣出日期 (YYYY-MM-DD)
            
        Returns:
            {
                'sell_date': '2026-01-06',
                'settlement_date': '2026-01-08',
                'business_days': 2,
                'calendar_days': 2,
                'skipped_days': [...]
            }
        """
        holidays = self.get_holidays()
        
        sell = datetime.strptime(sell_date, '%Y-%m-%d')
        current = sell
        business_days = 0
        skipped_days = []
        
        while business_days < 2:
            current += timedelta(days=1)
            current_str = current.strftime('%Y-%m-%d')
            weekday = current.weekday()
            
            # 週六(5)、週日(6) 或假日
            if weekday >= 5 or current_str in holidays:
                reason = '週末' if weekday >= 5 else '休市日'
                skipped_days.append({
                    'date': current_str,
                    'reason': reason,
                    'weekday': current.strftime('%A')
                })
            else:
                business_days += 1
        
        settlement_date = current.strftime('%Y-%m-%d')
        calendar_days = (current - sell).days
        
        return {
            'sell_date': sell_date,
            'settlement_date': settlement_date,
            'settlement_date_formatted': current.strftime('%Y年%m月%d日'),
            'settlement_weekday': ['週一', '週二', '週三', '週四', '週五', '週六', '週日'][current.weekday()],
            'business_days': 2,
            'calendar_days': calendar_days,
            'skipped_days': skipped_days
        }
    
    def get_holidays_list(self, year: int = None) -> List[dict]:
        """取得假日清單（含說明）"""
        if year is None:
            year = datetime.now().year
            
        holidays = self.get_holidays()
        result = []
        
        for h in sorted(holidays):
            if h.startswith(str(year)):
                date_obj = datetime.strptime(h, '%Y-%m-%d')
                result.append({
                    'date': h,
                    'formatted': date_obj.strftime('%Y年%m月%d日'),
                    'weekday': ['週一', '週二', '週三', '週四', '週五', '週六', '週日'][date_obj.weekday()]
                })
        
        return result


# 建立服務實例
holiday_service = HolidayService()