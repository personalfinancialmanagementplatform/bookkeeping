"""
智慧投資組合配置建議服務 - Portfolio Advisor (改進版)
檔案位置: backend/app/services/portfolio_advisor.py

功能：
1. 風險問卷評估（金管會標準 12 題）
2. 直接選擇風險偏好（保守/穩健/積極）
3. 根據投資目標調整配置
4. 推薦具體標的（台灣 ETF、個股、債券）
5. 自動計算投資金額分配
6. 支援自訂投資標的優先納入配置
7. 改進版：殖利率 + 資本增值 = 總報酬計算
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


# ============================================
# 列舉定義
# ============================================
class RiskLevel(Enum):
    """風險等級"""
    CONSERVATIVE = "conservative"      # 保守型
    MODERATE = "moderate"              # 穩健型
    AGGRESSIVE = "aggressive"          # 積極型


class InvestmentGoal(Enum):
    """投資目標"""
    RETIREMENT = "retirement"          # 退休規劃
    WEALTH_GROWTH = "wealth_growth"    # 財富增長
    INCOME = "income"                  # 穩定收益
    PRESERVATION = "preservation"      # 資產保值


# ============================================
# 資料結構
# ============================================
@dataclass
class AssetAllocation:
    """單一資產配置"""
    asset_type: str       # 資產類型: stocks/etf/bonds/cash
    symbol: str           # 標的代碼
    name: str             # 名稱
    weight: float         # 權重 (0-1)
    amount: float         # 建議金額
    reason: str           # 推薦理由
    expected_yield: float # 預估殖利率
    expected_growth: float = 0.0  # 預估資本增值
    expected_total: float = 0.0   # 預估總報酬


@dataclass
class AllocationResult:
    """配置建議結果"""
    total_amount: float
    risk_level: str
    risk_level_name: str
    goal: str
    allocations: List[AssetAllocation]
    summary: str
    warnings: List[str]
    expected_dividend_yield: float  # 預估殖利率
    expected_capital_growth: float  # 預估資本增值
    expected_total_yield: float     # 預估總報酬
    created_at: str


# ============================================
# 風險問卷系統（金管會標準版）
# ============================================
class RiskQuestionnaire:
    """
    風險評估問卷（金管會標準版）
    共 12 題，依據分數判斷風險屬性
    """
    
    QUESTIONS = [
        {
            'id': 1,
            'question': '您的年齡層',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '65 歲以上', 'score': 1},
                {'value': 2, 'label': '56~64 歲', 'score': 2},
                {'value': 3, 'label': '46~55 歲', 'score': 3},
                {'value': 4, 'label': '36~45 歲', 'score': 4},
                {'value': 5, 'label': '19~35 歲', 'score': 5},
                {'value': 6, 'label': '18 歲以下', 'score': 3}
            ]
        },
        {
            'id': 2,
            'question': '您曾使用過的理財工具',
            'type': 'multiple',
            'hint': '可複選',
            'options': [
                {'value': 1, 'label': '無使用理財工具', 'score': 0},
                {'value': 2, 'label': '儲蓄保險、定期存款、黃金、貨幣市場型基金', 'score': 1},
                {'value': 3, 'label': '債券類型相關的基金（如：債券型基金、債券型 ETF）', 'score': 2},
                {'value': 4, 'label': '其他類型基金（如：股票型基金）', 'score': 3},
                {'value': 5, 'label': '股票', 'score': 4},
                {'value': 6, 'label': '外匯交易（如：外匯保證金、外匯遠期交易）', 'score': 5},
                {'value': 7, 'label': '期貨或選擇權或其他衍生性金融商品', 'score': 6}
            ]
        },
        {
            'id': 3,
            'question': '投資債券類型相關商品之理財工具經驗',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '無經驗', 'score': 0},
                {'value': 2, 'label': '1 年以下', 'score': 1},
                {'value': 3, 'label': '1 年(含)~3 年', 'score': 2},
                {'value': 4, 'label': '3 年(含)~5 年', 'score': 3},
                {'value': 5, 'label': '5 年(含)以上', 'score': 4}
            ]
        },
        {
            'id': 4,
            'question': '投資其他非債券類型相關商品之理財工具經驗',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '無經驗', 'score': 0},
                {'value': 2, 'label': '1 年以下', 'score': 1},
                {'value': 3, 'label': '1 年(含)~3 年', 'score': 2},
                {'value': 4, 'label': '3 年(含)~5 年', 'score': 3},
                {'value': 5, 'label': '5 年(含)以上', 'score': 4}
            ]
        },
        {
            'id': 5,
            'question': '下列何者最符合您對投資理財工具的理解',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '對投資理財工具不熟悉，但有興趣進一步瞭解', 'score': 1},
                {'value': 2, 'label': '瞭解基本知識，例如股票與基金的分別', 'score': 2},
                {'value': 3, 'label': '瞭解基本知識，並明白分散投資及資產配置的重要性', 'score': 3},
                {'value': 4, 'label': '對投資理財工具及其投資風險有進一步的認識', 'score': 4},
                {'value': 5, 'label': '非常熟悉大部份投資理財工具，並明白影響風險和表現的各項因素', 'score': 5}
            ]
        },
        {
            'id': 6,
            'question': '每年可用於購買投資理財工具之金額（新台幣）',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '未滿 50 萬', 'score': 1},
                {'value': 2, 'label': '50 萬(含)以上~未滿 100 萬', 'score': 2},
                {'value': 3, 'label': '100 萬(含)以上~未滿 300 萬', 'score': 3},
                {'value': 4, 'label': '300 萬(含)以上', 'score': 4}
            ]
        },
        {
            'id': 7,
            'question': '請問您的備用金（現金及存款）相當於您幾個月的生活開銷？',
            'type': 'single',
            'hint': '在您考慮投資之前，建議先準備一筆可以隨時動用且足以因應不時之需的備用金',
            'options': [
                {'value': 1, 'label': '無備用金或無須負擔生活開銷', 'score': 0},
                {'value': 2, 'label': '3 個月以下', 'score': 1},
                {'value': 3, 'label': '超過(含)3 個月未達 6 個月', 'score': 2},
                {'value': 4, 'label': '超過(含)6 個月未達 1 年', 'score': 3},
                {'value': 5, 'label': '超過(含)1 年', 'score': 4},
                {'value': 6, 'label': '超過(含)3 年以上', 'score': 5}
            ]
        },
        {
            'id': 8,
            'question': '每年可承受的價格損失（含匯率風險）',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '無法接受虧損', 'score': 0},
                {'value': 2, 'label': '-5%', 'score': 1},
                {'value': 3, 'label': '-10%', 'score': 2},
                {'value': 4, 'label': '-15%', 'score': 3},
                {'value': 5, 'label': '-20%', 'score': 4}
            ]
        },
        {
            'id': 9,
            'question': '在達到預計投資期間時（例如 3 年、5 年），可承受的價格損失',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '無法接受虧損', 'score': 0},
                {'value': 2, 'label': '-5%', 'score': 1},
                {'value': 3, 'label': '-10%', 'score': 2},
                {'value': 4, 'label': '-15%', 'score': 3},
                {'value': 5, 'label': '-20%', 'score': 4}
            ]
        },
        {
            'id': 10,
            'question': '您的投資回報期望',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '避免資產損失', 'score': 1},
                {'value': 2, 'label': '資產每年穩定成長', 'score': 3},
                {'value': 3, 'label': '資產短期快速成長', 'score': 5}
            ]
        },
        {
            'id': 11,
            'question': '就長期投資而言，您期望每年平均投資報酬率',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '1%(含)~5%', 'score': 1},
                {'value': 2, 'label': '5%(含)~10%', 'score': 2},
                {'value': 3, 'label': '10%(含)~15%', 'score': 3},
                {'value': 4, 'label': '15%(含)~20%', 'score': 4}
            ]
        },
        {
            'id': 12,
            'question': '當投資發生虧損或達到停損點時會採取的處理方式',
            'type': 'single',
            'options': [
                {'value': 1, 'label': '立即賣出', 'score': 1},
                {'value': 2, 'label': '先賣出一半', 'score': 2},
                {'value': 3, 'label': '虧損未達 6 個月就賣掉', 'score': 3},
                {'value': 4, 'label': '虧損已經 6 個月以上才考慮出售', 'score': 4},
                {'value': 5, 'label': '持有 1 年以上', 'score': 5},
                {'value': 6, 'label': '持有至回本', 'score': 3}
            ]
        }
    ]
    
    # 風險等級說明（金管會標準）
    RISK_PROFILES = {
        'conservative': {
            'name': '保守型',
            'description': '您屬於風險趨避者，通常期望避免投資本金之損失，但仍願意承受少量風險以增加投資報酬；投資主要為風險等級較低之商品。',
            'suitable_rr': ['RR1', 'RR2'],
            'suitable_rr_desc': '低風險(RR1)及中低風險(RR2)之投資標的',
            'target_return': (5, 8)
        },
        'moderate': {
            'name': '穩健型',
            'description': '您屬於風險中立者，願意承擔部分風險以增加投資報酬；為了獲得提高投資報酬之機會，可以接受投資包含不同風險等級之商品。',
            'suitable_rr': ['RR1', 'RR2', 'RR3'],
            'suitable_rr_desc': '低風險(RR1)、中低風險(RR2)、中度風險(RR3)',
            'target_return': (8, 12)
        },
        'aggressive': {
            'name': '積極型',
            'description': '您屬於風險追求者，願意承擔相當程度風險以增加投資報酬；可以接受將所有資金投資於風險較高之商品，藉以獲取較高投資報酬。',
            'suitable_rr': ['RR1', 'RR2', 'RR3', 'RR4', 'RR5'],
            'suitable_rr_desc': '可依個人需求選擇低風險(RR1)至高風險(RR5)的任何投資標的',
            'target_return': (12, 20)
        }
    }
    
    @classmethod
    def get_questions(cls):
        """取得所有問題"""
        return cls.QUESTIONS
    
    @classmethod
    def calculate_risk_level(cls, answers: dict) -> dict:
        """
        計算風險等級
        """
        total_score = 0
        max_score = 0
        details = []
        
        for question in cls.QUESTIONS:
            q_id = question['id']
            answer = answers.get(q_id) or answers.get(str(q_id))
            
            if answer is None:
                continue
            
            question_score = 0
            
            if question['type'] == 'multiple':
                if isinstance(answer, list):
                    for opt in question['options']:
                        if opt['value'] in answer:
                            question_score = max(question_score, opt['score'])
                else:
                    for opt in question['options']:
                        if opt['value'] == answer:
                            question_score = opt['score']
                            break
                max_score += max(opt['score'] for opt in question['options'])
            else:
                for opt in question['options']:
                    if opt['value'] == answer:
                        question_score = opt['score']
                        break
                max_score += max(opt['score'] for opt in question['options'])
            
            total_score += question_score
            details.append({
                'question_id': q_id,
                'answer': answer,
                'score': question_score
            })
        
        score_percent = (total_score / max_score * 100) if max_score > 0 else 0
        
        if score_percent < 35:
            risk_level = 'conservative'
        elif score_percent < 65:
            risk_level = 'moderate'
        else:
            risk_level = 'aggressive'
        
        profile = cls.RISK_PROFILES[risk_level]
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'score_percent': round(score_percent, 1),
            'risk_level': risk_level,
            'risk_level_name': profile['name'],
            'description': profile['description'],
            'suitable_rr': profile['suitable_rr'],
            'suitable_rr_desc': profile['suitable_rr_desc'],
            'target_return': profile['target_return'],
            'details': details
        }
    
    @classmethod
    def get_risk_profiles(cls):
        """取得所有風險等級說明"""
        return cls.RISK_PROFILES


# ============================================
# 改進版：標的預估報酬資料庫（殖利率 + 資本增值）
# ============================================
ASSET_EXPECTED_RETURNS = {
    # === ETF - 大盤型 ===
    '0050': {
        'name': '元大台灣50', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 3.5, 'capital_growth': 8.0, 'total': 11.5,
        'description': '追蹤台灣市值前 50 大企業，長期穩健成長'
    },
    '006208': {
        'name': '富邦台50', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 3.3, 'capital_growth': 8.0, 'total': 11.3,
        'description': '低成本追蹤台灣50指數，管理費僅 0.15%'
    },
    
    # === ETF - 高股息 ===
    '0056': {
        'name': '元大高股息', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 6.5, 'capital_growth': 3.0, 'total': 9.5,
        'description': '精選高殖利率股票，適合追求股息收入'
    },
    '00878': {
        'name': '國泰永續高股息', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 7.0, 'capital_growth': 2.5, 'total': 9.5,
        'description': 'ESG 篩選 + 高股息策略，季配息'
    },
    '00713': {
        'name': '元大台灣高息低波', 'type': 'etf', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 6.0, 'capital_growth': 3.5, 'total': 9.5,
        'description': '低波動高股息，適合保守型投資人'
    },
    
    # === ETF - 月配息 ===
    '00919': {
        'name': '群益台灣精選高息', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 8.0, 'capital_growth': 2.0, 'total': 10.0,
        'description': '月配息 ETF，殖利率達 8% 以上'
    },
    '00929': {
        'name': '復華台灣科技優息', 'type': 'etf', 'risk': 'aggressive', 'rr': 'RR4',
        'dividend_yield': 7.5, 'capital_growth': 4.0, 'total': 11.5,
        'description': '科技股 + 月配息，兼顧成長與配息'
    },
    '00939': {
        'name': '統一台灣高息動能', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 6.8, 'capital_growth': 3.5, 'total': 10.3,
        'description': '動能策略 + 月配息'
    },
    '00940': {
        'name': '元大台灣價值高息', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 6.5, 'capital_growth': 3.0, 'total': 9.5,
        'description': '價值投資策略 + 月配息'
    },
    
    # === ETF - 債券型 ===
    '00679B': {
        'name': '元大美債20年', 'type': 'bonds', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 4.5, 'capital_growth': 0.5, 'total': 5.0,
        'description': '美國長天期公債 ETF，避險工具'
    },
    '00687B': {
        'name': '國泰20年美債', 'type': 'bonds', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 4.3, 'capital_growth': 0.5, 'total': 4.8,
        'description': '美國 20 年期公債'
    },
    '00720B': {
        'name': '元大投資級公司債', 'type': 'bonds', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 5.0, 'capital_growth': 0.3, 'total': 5.3,
        'description': '投資等級公司債，收益較公債高'
    },
    '00751B': {
        'name': '元大AAA至A公司債', 'type': 'bonds', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 4.8, 'capital_growth': 0.3, 'total': 5.1,
        'description': '高評級公司債，安全性高'
    },
    
    # === ETF - 產業型（高成長）===
    '00891': {
        'name': '中信關鍵半導體', 'type': 'etf', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 2.5, 'capital_growth': 15.0, 'total': 17.5,
        'description': '聚焦台灣半導體產業，成長潛力大'
    },
    '00892': {
        'name': '富邦台灣半導體', 'type': 'etf', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 2.3, 'capital_growth': 15.0, 'total': 17.3,
        'description': '台灣半導體產業 ETF'
    },
    '00881': {
        'name': '國泰台灣5G+', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 3.0, 'capital_growth': 10.0, 'total': 13.0,
        'description': '5G 通訊產業 ETF'
    },
    
    # === ETF - 海外 ===
    '00646': {
        'name': '元大S&P500', 'type': 'etf', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 1.5, 'capital_growth': 10.0, 'total': 11.5,
        'description': '追蹤美國 S&P 500 指數'
    },
    '00662': {
        'name': '富邦NASDAQ', 'type': 'etf', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 0.8, 'capital_growth': 15.0, 'total': 15.8,
        'description': '追蹤美國 NASDAQ 指數，科技股為主'
    },
    '00830': {
        'name': '國泰費城半導體', 'type': 'etf', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 0.5, 'capital_growth': 18.0, 'total': 18.5,
        'description': '追蹤費城半導體指數，全球半導體龍頭'
    },
    
    # === 股票 - 成長型 ===
    '2330': {
        'name': '台積電', 'type': 'stocks', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 1.8, 'capital_growth': 15.0, 'total': 16.8,
        'description': '全球晶圓代工龍頭，長期成長潛力'
    },
    '2454': {
        'name': '聯發科', 'type': 'stocks', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 3.5, 'capital_growth': 12.0, 'total': 15.5,
        'description': 'IC 設計龍頭，受惠 AI 趨勢'
    },
    '2382': {
        'name': '廣達', 'type': 'stocks', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 3.0, 'capital_growth': 20.0, 'total': 23.0,
        'description': 'AI 伺服器代工大廠，輝達合作夥伴'
    },
    '3443': {
        'name': '創意', 'type': 'stocks', 'risk': 'aggressive', 'rr': 'RR5',
        'dividend_yield': 2.0, 'capital_growth': 18.0, 'total': 20.0,
        'description': 'ASIC 設計服務，受惠 AI 客製化晶片'
    },
    '2379': {
        'name': '瑞昱', 'type': 'stocks', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 4.0, 'capital_growth': 10.0, 'total': 14.0,
        'description': '網通晶片大廠，配息穩定'
    },
    '2308': {
        'name': '台達電', 'type': 'stocks', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 2.5, 'capital_growth': 12.0, 'total': 14.5,
        'description': '電源管理龍頭，受惠電動車與資料中心'
    },
    '3034': {
        'name': '聯詠', 'type': 'stocks', 'risk': 'moderate', 'rr': 'RR4',
        'dividend_yield': 5.0, 'capital_growth': 10.0, 'total': 15.0,
        'description': '驅動 IC 龍頭，高配息'
    },
    
    # === 股票 - 穩健型 ===
    '2317': {
        'name': '鴻海', 'type': 'stocks', 'risk': 'moderate', 'rr': 'RR3',
        'dividend_yield': 5.0, 'capital_growth': 5.0, 'total': 10.0,
        'description': '全球最大 EMS 廠，穩定配息'
    },
    '2881': {
        'name': '富邦金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 5.5, 'capital_growth': 5.0, 'total': 10.5,
        'description': '金控龍頭，獲利穩健，配息佳'
    },
    '2882': {
        'name': '國泰金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 5.0, 'capital_growth': 4.0, 'total': 9.0,
        'description': '壽險龍頭，長期穩健'
    },
    '2884': {
        'name': '玉山金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 4.5, 'capital_growth': 5.0, 'total': 9.5,
        'description': '獲利成長穩定的金控'
    },
    '2886': {
        'name': '兆豐金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 5.2, 'capital_growth': 4.0, 'total': 9.2,
        'description': '官股金控，經營穩健，配息穩定'
    },
    '2891': {
        'name': '中信金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 5.8, 'capital_growth': 5.0, 'total': 10.8,
        'description': '獲利佳，配息率高'
    },
    '5880': {
        'name': '合庫金', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 5.5, 'capital_growth': 3.5, 'total': 9.0,
        'description': '官股金控，穩定配息'
    },
    
    # === 股票 - 防禦型 ===
    '1216': {
        'name': '統一', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 4.0, 'capital_growth': 3.0, 'total': 7.0,
        'description': '食品龍頭，防禦性標的'
    },
    '2412': {
        'name': '中華電', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR2',
        'dividend_yield': 4.5, 'capital_growth': 2.0, 'total': 6.5,
        'description': '電信龍頭，防禦性極佳'
    },
    '1301': {
        'name': '台塑', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 5.5, 'capital_growth': 2.0, 'total': 7.5,
        'description': '塑化龍頭，景氣循環股'
    },
    '9910': {
        'name': '豐泰', 'type': 'stocks', 'risk': 'conservative', 'rr': 'RR3',
        'dividend_yield': 4.0, 'capital_growth': 5.0, 'total': 9.0,
        'description': 'Nike 代工廠，獲利穩定'
    },
    
    # === 現金 ===
    'CASH': {
        'name': '現金 / 貨幣基金', 'type': 'cash', 'risk': 'conservative', 'rr': 'RR1',
        'dividend_yield': 1.5, 'capital_growth': 0.0, 'total': 1.5,
        'description': '保持流動性，作為緊急預備金'
    },
}


# ============================================
# 投資組合配置建議服務
# ============================================
class PortfolioAdvisor:
    """
    智慧配置建議系統（改進版）
    """
    
    # 資產配置模板（依風險等級）- 改進版
    ALLOCATION_TEMPLATES = {
        RiskLevel.CONSERVATIVE: {
            'bonds': 0.45,      # 債券 45%
            'etf': 0.30,        # ETF 30%（高股息、低波動）
            'stocks': 0.15,     # 股票 15%（防禦型）
            'cash': 0.10        # 現金 10%
        },
        RiskLevel.MODERATE: {
            'bonds': 0.20,      # 債券 20%
            'etf': 0.35,        # ETF 35%
            'stocks': 0.40,     # 股票 40%
            'cash': 0.05        # 現金 5%
        },
        RiskLevel.AGGRESSIVE: {
            'bonds': 0.10,      # 債券 10%
            'etf': 0.25,        # ETF 25%（科技、半導體）
            'stocks': 0.60,     # 股票 60%（成長型）
            'cash': 0.05        # 現金 5%
        }
    }
    
    # 風險等級對應的偏好標的
    RISK_PREFERRED_ASSETS = {
        RiskLevel.CONSERVATIVE: {
            'bonds': ['00679B', '00720B', '00751B', '00687B'],
            'etf': ['00713', '0056', '00878'],
            'stocks': ['2881', '2882', '2886', '5880', '2412', '1216'],
        },
        RiskLevel.MODERATE: {
            'bonds': ['00679B', '00720B'],
            'etf': ['0050', '006208', '0056', '00878', '00919', '00929'],
            'stocks': ['2330', '2317', '2881', '2886', '2379', '3034'],
        },
        RiskLevel.AGGRESSIVE: {
            'bonds': ['00679B'],
            'etf': ['0050', '00929', '00891', '00892', '00662', '00830'],
            'stocks': ['2330', '2454', '2382', '3443', '2308', '2317'],
        }
    }
    
    # 投資目標對應的調整
    GOAL_ADJUSTMENTS = {
        'retirement': {
            'bonds': 1.3, 'etf': 1.1, 'stocks': 0.7, 'cash': 1.2,
            'preferred': ['0056', '00878', '00919', '00713', '2886', '2891', '00679B']
        },
        'wealth_growth': {
            'bonds': 0.5, 'etf': 1.0, 'stocks': 1.4, 'cash': 0.5,
            'preferred': ['2330', '2454', '2382', '0050', '00891', '00662']
        },
        'income': {
            'bonds': 1.2, 'etf': 1.2, 'stocks': 0.8, 'cash': 0.8,
            'preferred': ['0056', '00878', '00919', '00929', '2881', '2886', '00720B']
        },
        'preservation': {
            'bonds': 1.5, 'etf': 0.8, 'stocks': 0.5, 'cash': 1.5,
            'preferred': ['00679B', '00720B', '00751B', '00713', '2412', '1216']
        }
    }
    
    RISK_NAMES = {
        RiskLevel.CONSERVATIVE: '保守型',
        RiskLevel.MODERATE: '穩健型',
        RiskLevel.AGGRESSIVE: '積極型'
    }
    
    GOAL_NAMES = {
        'retirement': '退休規劃',
        'wealth_growth': '財富增長',
        'income': '穩定收益',
        'preservation': '資產保值'
    }
    
    def __init__(self):
        self.questionnaire = RiskQuestionnaire()
        self.asset_data = ASSET_EXPECTED_RETURNS
    
    def generate_recommendation(
        self,
        amount: float,
        risk_level: str = 'moderate',
        goal: str = 'wealth_growth',
        age: Optional[int] = None,
        existing_holdings: Optional[List[Dict]] = None,
        custom_assets: Optional[List[str]] = None
    ) -> AllocationResult:
        """
        產生投資組合配置建議
        """
        # 1. 解析風險等級
        try:
            risk = RiskLevel(risk_level)
        except:
            risk = RiskLevel.MODERATE
        
        # 2. 根據年齡調整風險
        if age:
            risk = self._adjust_risk_by_age(risk, age)
        
        # 3. 取得基礎配置
        base_allocation = self.ALLOCATION_TEMPLATES[risk].copy()
        
        # 4. 根據目標微調
        base_allocation = self._adjust_by_goal(base_allocation, goal)
        
        # 5. 選擇具體標的
        existing_symbols = {h.get('symbol') for h in (existing_holdings or [])}
        allocations = self._select_assets(
            amount, 
            base_allocation, 
            risk,
            goal,
            existing_symbols,
            custom_assets or []
        )
        
        # 6. 計算預估報酬（改進版：殖利率 + 資本增值）
        returns = self._calculate_expected_returns(allocations)
        
        # 7. 產生警示
        warnings = self._generate_warnings(amount, allocations, risk, age)
        
        # 8. 產生摘要
        summary = self._generate_summary(amount, risk, goal, returns)
        
        return AllocationResult(
            total_amount=amount,
            risk_level=risk.value,
            risk_level_name=self.RISK_NAMES[risk],
            goal=goal,
            allocations=allocations,
            summary=summary,
            warnings=warnings,
            expected_dividend_yield=returns['dividend_yield'],
            expected_capital_growth=returns['capital_growth'],
            expected_total_yield=returns['total'],
            created_at=datetime.now().isoformat()
        )
    
    def _adjust_risk_by_age(self, risk: RiskLevel, age: int) -> RiskLevel:
        """根據年齡調整風險等級"""
        if age >= 60:
            return RiskLevel.CONSERVATIVE
        elif age >= 50 and risk == RiskLevel.AGGRESSIVE:
            return RiskLevel.MODERATE
        elif age < 30 and risk == RiskLevel.CONSERVATIVE:
            return RiskLevel.MODERATE
        return risk
    
    def _adjust_by_goal(self, allocation: Dict, goal: str) -> Dict:
        """根據投資目標調整配置"""
        adjustments = self.GOAL_ADJUSTMENTS.get(goal, {})
        adjusted = {}
        
        for asset_type, weight in allocation.items():
            multiplier = adjustments.get(asset_type, 1.0)
            adjusted[asset_type] = weight * multiplier
        
        # 正規化確保總和為 1
        total = sum(adjusted.values())
        return {k: v/total for k, v in adjusted.items()}
    
    def _select_assets(
        self,
        amount: float,
        allocation_weights: Dict[str, float],
        risk: RiskLevel,
        goal: str,
        existing_symbols: set,
        custom_assets: List[str] = None
    ) -> List[AssetAllocation]:
        """選擇具體投資標的（改進版）"""
        allocations = []
        custom_assets = custom_assets or []
        used_symbols = set(existing_symbols)
        
        # === 優先處理自訂標的 ===
        custom_weight_used = 0
        if custom_assets:
            custom_per_weight = min(0.20, 0.6 / len(custom_assets))
            
            for symbol in custom_assets:
                asset_info = self.asset_data.get(symbol)
                if asset_info and symbol not in used_symbols:
                    custom_amount = amount * custom_per_weight
                    allocations.append(AssetAllocation(
                        asset_type=asset_info.get('type', 'etf'),
                        symbol=symbol,
                        name=asset_info['name'],
                        weight=round(custom_per_weight, 4),
                        amount=round(custom_amount, 0),
                        reason=f"您指定的標的：{asset_info.get('description', '')}",
                        expected_yield=asset_info.get('dividend_yield', 3.0),
                        expected_growth=asset_info.get('capital_growth', 5.0),
                        expected_total=asset_info.get('total', 8.0)
                    ))
                    custom_weight_used += custom_per_weight
                    used_symbols.add(symbol)
        
        remaining_weight = 1 - custom_weight_used
        
        # === 取得偏好標的 ===
        preferred = self.RISK_PREFERRED_ASSETS.get(risk, {})
        goal_preferred = self.GOAL_ADJUSTMENTS.get(goal, {}).get('preferred', [])
        
        # === 依類別選擇標的 ===
        for asset_type, weight in allocation_weights.items():
            adjusted_weight = weight * remaining_weight
            
            if adjusted_weight <= 0.01:
                continue
            
            asset_amount = amount * adjusted_weight
            
            # 現金部位
            if asset_type == 'cash':
                cash_info = self.asset_data.get('CASH', {})
                allocations.append(AssetAllocation(
                    asset_type='cash',
                    symbol='CASH',
                    name='現金 / 貨幣基金',
                    weight=round(adjusted_weight, 4),
                    amount=round(asset_amount, 0),
                    reason='保持流動性，作為緊急預備金或等待投資機會',
                    expected_yield=1.5,
                    expected_growth=0.0,
                    expected_total=1.5
                ))
                continue
            
            # 取得該類別的候選標的
            type_preferred = preferred.get(asset_type, [])
            
            # 結合目標偏好
            candidates = []
            for symbol in goal_preferred:
                if symbol in type_preferred and symbol not in used_symbols:
                    candidates.append(symbol)
            for symbol in type_preferred:
                if symbol not in candidates and symbol not in used_symbols:
                    candidates.append(symbol)
            
            if not candidates:
                continue
            
            # 選擇 1-2 檔分散風險
            num_assets = min(2, len(candidates)) if asset_amount >= 20000 else 1
            selected = candidates[:num_assets]
            
            per_asset_weight = adjusted_weight / num_assets
            per_asset_amount = asset_amount / num_assets
            
            for symbol in selected:
                asset_info = self.asset_data.get(symbol, {})
                if asset_info:
                    allocations.append(AssetAllocation(
                        asset_type=asset_type,
                        symbol=symbol,
                        name=asset_info.get('name', symbol),
                        weight=round(per_asset_weight, 4),
                        amount=round(per_asset_amount, 0),
                        reason=self._get_recommendation_reason(symbol, risk, goal),
                        expected_yield=asset_info.get('dividend_yield', 3.0),
                        expected_growth=asset_info.get('capital_growth', 5.0),
                        expected_total=asset_info.get('total', 8.0)
                    ))
                    used_symbols.add(symbol)
        
        # 按權重排序
        allocations.sort(key=lambda x: x.weight, reverse=True)
        
        return allocations
    
    def _calculate_expected_returns(self, allocations: List[AssetAllocation]) -> Dict:
        """計算預估報酬（改進版：殖利率 + 資本增值）"""
        if not allocations:
            return {'dividend_yield': 0, 'capital_growth': 0, 'total': 0}
        
        total_weight = sum(a.weight for a in allocations)
        
        if total_weight == 0:
            return {'dividend_yield': 0, 'capital_growth': 0, 'total': 0}
        
        weighted_dividend = sum(a.expected_yield * a.weight for a in allocations) / total_weight
        weighted_growth = sum(a.expected_growth * a.weight for a in allocations) / total_weight
        weighted_total = sum(a.expected_total * a.weight for a in allocations) / total_weight
        
        return {
            'dividend_yield': round(weighted_dividend, 2),
            'capital_growth': round(weighted_growth, 2),
            'total': round(weighted_total, 2)
        }
    
    def _get_recommendation_reason(self, symbol: str, risk: RiskLevel, goal: str) -> str:
        """生成推薦理由"""
        asset_info = self.asset_data.get(symbol, {})
        base_reason = asset_info.get('description', '')
        risk_name = self.RISK_NAMES.get(risk, '穩健型')
        goal_name = self.GOAL_NAMES.get(goal, '財富增長')
        
        reasons = {
            '0050': f"台灣市值前50大企業，分散風險的核心配置，適合{risk_name}投資人長期持有。",
            '006208': "追蹤台灣50指數，管理費極低(0.15%)，適合長期定期定額。",
            '0056': f"高股息策略，殖利率約6-7%，提供穩定現金流，符合{goal_name}目標。",
            '00878': "結合ESG永續與高股息，季配息，近年最受歡迎的ETF之一。",
            '00713': "高息低波策略，適合保守型投資人，降低投資組合波動。",
            '00919': "月月配息，殖利率達8%以上，適合追求穩定現金流。",
            '00929': "科技股月配息，兼顧成長性與配息收益。",
            '00679B': f"美國公債ETF，與股市負相關，{risk_name}配置中重要的避險部位。",
            '00720B': "投資級公司債，收益率比公債高，信用風險可控。",
            '00891': "聚焦台灣半導體產業，受惠AI趨勢，成長潛力大。",
            '00662': "追蹤NASDAQ指數，掌握美國科技股成長機會。",
            '00830': "費城半導體指數，全球半導體龍頭一網打盡。",
            '2330': f"全球晶圓代工龍頭，技術領先，{risk_name}投資人的核心持股。",
            '2454': "IC設計龍頭，受惠AI晶片需求，成長潛力佳。",
            '2382': "AI伺服器代工大廠，輝達合作夥伴，獲利大爆發。",
            '2317': "全球EMS龍頭，積極轉型電動車與AI伺服器，配息穩定。",
            '2881': "金控龍頭，獲利穩健，配息率高，適合穩健型投資人。",
            '2882': "壽險龍頭，長期經營穩健，配息穩定。",
            '2886': "官股金控，經營穩健，配息穩定，防禦性佳。",
            '2891': "金控獲利佳，配息率高，股價波動較小。",
            '2412': "電信龍頭，防禦性極佳，配息穩定，適合保守型配置。",
            '1216': "食品業龍頭，民生必需品，景氣影響小，適合資產保值。",
        }
        
        return reasons.get(symbol, f"{asset_info.get('name', symbol)}：{base_reason}")
    
    def _generate_warnings(
        self,
        amount: float,
        allocations: List[AssetAllocation],
        risk: RiskLevel,
        age: Optional[int] = None
    ) -> List[str]:
        """產生投資警示"""
        warnings = []
        
        if amount < 10000:
            warnings.append("投資金額較小，建議優先考慮 ETF 以降低單一股票風險")
        
        if amount > 1000000:
            warnings.append("投資金額較大，建議分批進場以降低時點風險")
        
        stock_weight = sum(a.weight for a in allocations if a.asset_type == 'stocks')
        if stock_weight > 0.5:
            warnings.append("股票配置超過 50%，請留意市場波動風險")
        
        if risk == RiskLevel.AGGRESSIVE:
            warnings.append("積極型配置可能面臨較大短期波動，建議有 3 年以上投資期間")
        
        if age:
            if age < 25 and risk == RiskLevel.CONSERVATIVE:
                warnings.append("您的年齡較輕，可考慮承擔稍高風險以追求更好報酬")
            elif age >= 60 and risk == RiskLevel.AGGRESSIVE:
                warnings.append("考量您的年齡，建議適度降低高風險資產比例")
        
        warnings.append("以上為系統建議，投資前請審慎評估個人財務狀況")
        warnings.append("投資一定有風險，基金投資有賺有賠，申購前應詳閱公開說明書")
        
        return warnings
    
    def _generate_summary(
        self,
        amount: float,
        risk: RiskLevel,
        goal: str,
        returns: Dict
    ) -> str:
        """產生配置摘要（改進版）"""
        risk_name = self.RISK_NAMES.get(risk, '穩健型')
        goal_name = self.GOAL_NAMES.get(goal, '財富增長')
        
        target_return = RiskQuestionnaire.RISK_PROFILES.get(risk.value, {}).get('target_return', (8, 12))
        target_low, target_high = target_return
        actual = returns['total']
        
        if actual >= target_high:
            assessment = "超越目標範圍"
        elif actual >= target_low:
            assessment = "符合目標範圍"
        else:
            assessment = "略低於目標"
        
        return (
            f"根據您的「{risk_name}」風險偏好和「{goal_name}」投資目標，"
            f"建議將 NT$ {amount:,.0f} 進行多元配置。"
            f"預估整體配置年化殖利率約 {returns['total']:.1f}%。"
        )
    
    def get_quick_allocation(self, amount: float, profile: str = 'balanced') -> Dict:
        """快速配置建議（預設模板）"""
        profiles = {
            'conservative': {
                'name': '保守配置',
                'allocations': [
                    {'symbol': '00713', 'name': '元大台灣高息低波', 'type': 'etf', 'weight': 0.30, 'total_return': 9.5},
                    {'symbol': '00679B', 'name': '元大美債20年', 'type': 'bonds', 'weight': 0.45, 'total_return': 5.0},
                    {'symbol': '2886', 'name': '兆豐金', 'type': 'stocks', 'weight': 0.15, 'total_return': 9.2},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.10, 'total_return': 1.5}
                ]
            },
            'balanced': {
                'name': '平衡配置',
                'allocations': [
                    {'symbol': '0050', 'name': '元大台灣50', 'type': 'etf', 'weight': 0.30, 'total_return': 11.5},
                    {'symbol': '00878', 'name': '國泰永續高股息', 'type': 'etf', 'weight': 0.25, 'total_return': 9.5},
                    {'symbol': '2881', 'name': '富邦金', 'type': 'stocks', 'weight': 0.20, 'total_return': 10.5},
                    {'symbol': '00679B', 'name': '元大美債20年', 'type': 'bonds', 'weight': 0.20, 'total_return': 5.0},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.05, 'total_return': 1.5}
                ]
            },
            'growth': {
                'name': '成長配置',
                'allocations': [
                    {'symbol': '2330', 'name': '台積電', 'type': 'stocks', 'weight': 0.30, 'total_return': 16.8},
                    {'symbol': '0050', 'name': '元大台灣50', 'type': 'etf', 'weight': 0.25, 'total_return': 11.5},
                    {'symbol': '00929', 'name': '復華台灣科技優息', 'type': 'etf', 'weight': 0.20, 'total_return': 11.5},
                    {'symbol': '2317', 'name': '鴻海', 'type': 'stocks', 'weight': 0.15, 'total_return': 10.0},
                    {'symbol': '00679B', 'name': '元大美債20年', 'type': 'bonds', 'weight': 0.05, 'total_return': 5.0},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.05, 'total_return': 1.5}
                ]
            }
        }
        
        selected = profiles.get(profile, profiles['balanced'])
        
        # 計算預估總報酬
        total_return = sum(
            item['weight'] * item['total_return'] 
            for item in selected['allocations']
        )
        
        return {
            'total_amount': amount,
            'profile': profile,
            'profile_name': selected['name'],
            'expected_total_yield': round(total_return, 2),
            'allocations': [
                {
                    **item,
                    'weight_percent': f"{item['weight']*100:.0f}%",
                    'amount': round(amount * item['weight'], 0)
                }
                for item in selected['allocations']
            ]
        }
    
    def to_dict(self, result: AllocationResult) -> Dict:
        """將結果轉換為字典格式"""
        return {
            'total_amount': result.total_amount,
            'risk_level': result.risk_level,
            'risk_level_name': result.risk_level_name,
            'goal': result.goal,
            'summary': result.summary,
            'expected_dividend_yield': result.expected_dividend_yield,
            'expected_capital_growth': result.expected_capital_growth,
            'expected_total_yield': result.expected_total_yield,
            'warnings': result.warnings,
            'created_at': result.created_at,
            'allocations': [
                {
                    'asset_type': a.asset_type,
                    'symbol': a.symbol,
                    'name': a.name,
                    'weight': a.weight,
                    'weight_percent': f"{a.weight*100:.1f}%",
                    'amount': a.amount,
                    'reason': a.reason,
                    'expected_yield': a.expected_yield,
                    'expected_growth': a.expected_growth,
                    'expected_total': a.expected_total
                }
                for a in result.allocations
            ]
        }


# ============================================
# 建立單例服務
# ============================================
portfolio_advisor = PortfolioAdvisor()