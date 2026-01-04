"""
智慧投資組合配置建議服務 - Portfolio Advisor
檔案位置: backend/app/services/portfolio_advisor.py

功能：
1. 風險問卷評估（金管會標準 12 題）
2. 直接選擇風險偏好（保守/穩健/積極）
3. 根據投資目標調整配置
4. 推薦具體標的（台灣 ETF、個股、債券）
5. 自動計算投資金額分配
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
    expected_total_yield: float
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
            'suitable_rr_desc': '低風險(RR1)及中低風險(RR2)之投資標的'
        },
        'moderate': {
            'name': '穩健型',
            'description': '您屬於風險中立者，願意承擔部分風險以增加投資報酬；為了獲得提高投資報酬之機會，可以接受投資包含不同風險等級之商品。',
            'suitable_rr': ['RR1', 'RR2', 'RR3'],
            'suitable_rr_desc': '低風險(RR1)、中低風險(RR2)、中度風險(RR3)'
        },
        'aggressive': {
            'name': '積極型',
            'description': '您屬於風險追求者，願意承擔相當程度風險以增加投資報酬；可以接受將所有資金投資於風險較高之商品，藉以獲取較高投資報酬。',
            'suitable_rr': ['RR1', 'RR2', 'RR3', 'RR4', 'RR5'],
            'suitable_rr_desc': '可依個人需求選擇低風險(RR1)至高風險(RR5)的任何投資標的'
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
        
        Args:
            answers: {1: 5, 2: [3, 5], 3: 3, ...} 
                     單選題為單一值，複選題為列表
        
        Returns:
            包含分數和風險等級的字典
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
                # 複選題：取最高分
                if isinstance(answer, list):
                    for opt in question['options']:
                        if opt['value'] in answer:
                            question_score = max(question_score, opt['score'])
                else:
                    # 單一值也處理
                    for opt in question['options']:
                        if opt['value'] == answer:
                            question_score = opt['score']
                            break
                max_score += max(opt['score'] for opt in question['options'])
            else:
                # 單選題
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
        
        # 計算百分比來判斷風險等級
        # 最高分約 55 分，保守型 < 35%，穩健型 35-65%，積極型 > 65%
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
            'details': details
        }
    
    @classmethod
    def get_risk_profiles(cls):
        """取得所有風險等級說明"""
        return cls.RISK_PROFILES


# ============================================
# 投資組合配置建議服務
# ============================================
class PortfolioAdvisor:
    """
    智慧配置建議系統
    """
    
    # 資產配置模板（依風險等級）
    ALLOCATION_TEMPLATES = {
        RiskLevel.CONSERVATIVE: {
            'bonds': 0.50,      # 債券 50%
            'etf': 0.25,        # ETF 25%
            'stocks': 0.15,     # 股票 15%
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
            'etf': 0.25,        # ETF 25%
            'stocks': 0.60,     # 股票 60%
            'cash': 0.05        # 現金 5%
        }
    }
    
    # 推薦標的資料庫
    RECOMMENDED_ASSETS = {
        'etf': [
            {
                'symbol': '0050', 'name': '元大台灣50', 
                'risk': 'moderate', 'yield': 3.5,
                'description': '追蹤台灣市值前 50 大企業，長期穩健成長'
            },
            {
                'symbol': '0056', 'name': '元大高股息',
                'risk': 'moderate', 'yield': 5.5,
                'description': '精選高殖利率股票，適合追求股息收入'
            },
            {
                'symbol': '006208', 'name': '富邦台50',
                'risk': 'moderate', 'yield': 3.2,
                'description': '低成本追蹤台灣50指數'
            },
            {
                'symbol': '00878', 'name': '國泰永續高股息',
                'risk': 'moderate', 'yield': 5.0,
                'description': 'ESG 篩選 + 高股息策略'
            },
            {
                'symbol': '00713', 'name': '元大台灣高息低波',
                'risk': 'conservative', 'yield': 4.8,
                'description': '低波動高股息，適合保守型投資人'
            },
            {
                'symbol': '00919', 'name': '群益台灣精選高息',
                'risk': 'moderate', 'yield': 8.0,
                'description': '月配息 ETF，高殖利率'
            },
            {
                'symbol': '00929', 'name': '復華台灣科技優息',
                'risk': 'aggressive', 'yield': 6.5,
                'description': '科技股 + 月配息'
            },
        ],
        'stocks': [
            {
                'symbol': '2330', 'name': '台積電',
                'risk': 'moderate', 'yield': 2.0,
                'description': '全球晶圓代工龍頭，長期成長潛力'
            },
            {
                'symbol': '2317', 'name': '鴻海',
                'risk': 'moderate', 'yield': 4.5,
                'description': '全球最大 EMS 廠，穩定配息'
            },
            {
                'symbol': '2454', 'name': '聯發科',
                'risk': 'aggressive', 'yield': 3.0,
                'description': 'IC 設計龍頭，受惠 AI 趨勢'
            },
            {
                'symbol': '2382', 'name': '廣達',
                'risk': 'aggressive', 'yield': 3.5,
                'description': 'AI 伺服器代工大廠'
            },
            {
                'symbol': '2881', 'name': '富邦金',
                'risk': 'conservative', 'yield': 5.0,
                'description': '金控龍頭，穩定配息'
            },
            {
                'symbol': '2882', 'name': '國泰金',
                'risk': 'conservative', 'yield': 4.5,
                'description': '壽險龍頭，長期穩健'
            },
            {
                'symbol': '1216', 'name': '統一',
                'risk': 'conservative', 'yield': 4.0,
                'description': '食品龍頭，防禦性標的'
            },
        ],
        'bonds': [
            {
                'symbol': '00679B', 'name': '元大美債20年',
                'risk': 'conservative', 'yield': 4.0,
                'description': '美國長天期公債 ETF，避險工具'
            },
            {
                'symbol': '00687B', 'name': '國泰20年美債',
                'risk': 'conservative', 'yield': 4.2,
                'description': '美國 20 年期公債'
            },
            {
                'symbol': '00720B', 'name': '元大投資級公司債',
                'risk': 'conservative', 'yield': 4.5,
                'description': '投資等級公司債，收益較高'
            },
            {
                'symbol': '00751B', 'name': '元大AAA至A公司債',
                'risk': 'conservative', 'yield': 4.3,
                'description': '高評級公司債'
            },
        ]
    }
    
    # 風險等級名稱
    RISK_NAMES = {
        RiskLevel.CONSERVATIVE: '保守型',
        RiskLevel.MODERATE: '穩健型',
        RiskLevel.AGGRESSIVE: '積極型'
    }
    
    # 投資目標名稱
    GOAL_NAMES = {
        'retirement': '退休規劃',
        'wealth_growth': '財富增長',
        'income': '穩定收益',
        'preservation': '資產保值'
    }
    
    def __init__(self):
        self.questionnaire = RiskQuestionnaire()
    
    # ==========================================
    # 主要 API：產生配置建議
    # ==========================================
    def generate_recommendation(
        self,
        amount: float,
        risk_level: str = 'moderate',
        goal: str = 'wealth_growth',
        age: Optional[int] = None,
        existing_holdings: Optional[List[Dict]] = None
    ) -> AllocationResult:
        """
        產生投資組合配置建議
        
        Args:
            amount: 投資金額 (NT$)
            risk_level: 風險等級 (conservative/moderate/aggressive)
            goal: 投資目標
            age: 年齡（用於微調）
            existing_holdings: 現有持倉（避免重複推薦）
        
        Returns:
            AllocationResult 完整配置建議
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
        allocations = self._select_assets(amount, base_allocation, risk, existing_symbols)
        
        # 6. 計算預估總殖利率
        total_yield = sum(a.weight * a.expected_yield for a in allocations)
        
        # 7. 產生警示
        warnings = self._generate_warnings(amount, allocations, risk)
        
        # 8. 產生摘要
        summary = self._generate_summary(amount, risk, goal, total_yield)
        
        return AllocationResult(
            total_amount=amount,
            risk_level=risk.value,
            risk_level_name=self.RISK_NAMES[risk],
            goal=goal,
            allocations=allocations,
            summary=summary,
            warnings=warnings,
            expected_total_yield=round(total_yield, 2),
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
        adjusted = allocation.copy()
        
        if goal == 'income':
            # 收益導向：增加債券
            adjusted['bonds'] = min(adjusted['bonds'] + 0.15, 0.6)
            adjusted['stocks'] = max(adjusted['stocks'] - 0.15, 0.1)
        elif goal == 'wealth_growth':
            # 成長導向：增加股票
            adjusted['stocks'] = min(adjusted['stocks'] + 0.1, 0.7)
            adjusted['bonds'] = max(adjusted['bonds'] - 0.1, 0.05)
        elif goal == 'preservation':
            # 保值導向：增加債券和現金
            adjusted['bonds'] = min(adjusted['bonds'] + 0.2, 0.6)
            adjusted['cash'] = min(adjusted['cash'] + 0.1, 0.2)
            adjusted['stocks'] = max(adjusted['stocks'] - 0.3, 0.1)
        
        # 正規化確保總和為 1
        total = sum(adjusted.values())
        return {k: v/total for k, v in adjusted.items()}
    
    def _select_assets(
        self,
        amount: float,
        allocation_weights: Dict[str, float],
        risk: RiskLevel,
        existing_symbols: set
    ) -> List[AssetAllocation]:
        """選擇具體投資標的"""
        allocations = []
        
        risk_filter = {
            RiskLevel.CONSERVATIVE: ['conservative'],
            RiskLevel.MODERATE: ['conservative', 'moderate'],
            RiskLevel.AGGRESSIVE: ['conservative', 'moderate', 'aggressive']
        }
        allowed_risks = risk_filter.get(risk, ['moderate'])
        
        for asset_type, weight in allocation_weights.items():
            if weight <= 0.01:
                continue
            
            asset_amount = amount * weight
            
            # 現金部位
            if asset_type == 'cash':
                allocations.append(AssetAllocation(
                    asset_type='cash',
                    symbol='CASH',
                    name='現金 / 貨幣基金',
                    weight=weight,
                    amount=round(asset_amount, 0),
                    reason='保持流動性，作為緊急預備金或等待投資機會',
                    expected_yield=1.5
                ))
                continue
            
            # 取得該類別標的
            candidates = self.RECOMMENDED_ASSETS.get(asset_type, [])
            
            # 根據風險等級過濾
            filtered = [c for c in candidates if c['risk'] in allowed_risks]
            
            # 排除已持有
            filtered = [c for c in filtered if c['symbol'] not in existing_symbols]
            
            if not filtered:
                filtered = candidates[:2]
            
            # 選擇 1-2 檔分散風險
            num_assets = min(2, len(filtered)) if asset_amount >= 30000 else 1
            selected = filtered[:num_assets]
            
            per_asset_weight = weight / num_assets
            per_asset_amount = asset_amount / num_assets
            
            for asset in selected:
                allocations.append(AssetAllocation(
                    asset_type=asset_type,
                    symbol=asset['symbol'],
                    name=asset['name'],
                    weight=round(per_asset_weight, 4),
                    amount=round(per_asset_amount, 0),
                    reason=asset['description'],
                    expected_yield=asset['yield']
                ))
        
        return allocations
    
    def _generate_warnings(
        self,
        amount: float,
        allocations: List[AssetAllocation],
        risk: RiskLevel
    ) -> List[str]:
        """產生投資警示"""
        warnings = []
        
        if amount < 10000:
            warnings.append("⚠️ 投資金額較小，建議優先考慮 ETF 以降低單一股票風險")
        
        if amount > 1000000:
            warnings.append("⚠️ 投資金額較大，建議分批進場以降低時點風險")
        
        stock_weight = sum(a.weight for a in allocations if a.asset_type == 'stocks')
        if stock_weight > 0.5:
            warnings.append("⚠️ 股票配置超過 50%，請留意市場波動風險")
        
        if risk == RiskLevel.AGGRESSIVE:
            warnings.append("⚠️ 積極型配置可能面臨較大短期波動，建議有 3 年以上投資期間")
        
        warnings.append("📋 以上為系統建議，投資前請審慎評估個人財務狀況")
        warnings.append("📋 投資一定有風險，基金投資有賺有賠，申購前應詳閱公開說明書")
        
        return warnings
    
    def _generate_summary(
        self,
        amount: float,
        risk: RiskLevel,
        goal: str,
        total_yield: float
    ) -> str:
        """產生配置摘要"""
        risk_name = self.RISK_NAMES.get(risk, '穩健型')
        goal_name = self.GOAL_NAMES.get(goal, '財富增長')
        
        return (
            f"根據您的「{risk_name}」風險偏好和「{goal_name}」投資目標，"
            f"建議將 NT$ {amount:,.0f} 進行多元配置。"
            f"預估整體配置年化殖利率約 {total_yield:.1f}%。"
        )
    
    # ==========================================
    # 快速配置（預設模板）
    # ==========================================
    def get_quick_allocation(self, amount: float, profile: str = 'balanced') -> Dict:
        """
        快速配置建議（預設模板）
        
        Args:
            amount: 投資金額
            profile: 'conservative' / 'balanced' / 'growth'
        """
        profiles = {
            'conservative': {
                'name': '保守配置',
                'allocations': [
                    {'symbol': '00713', 'name': '元大台灣高息低波', 'type': 'etf', 'weight': 0.35},
                    {'symbol': '00679B', 'name': '元大美債20年', 'type': 'bonds', 'weight': 0.45},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.20}
                ]
            },
            'balanced': {
                'name': '平衡配置',
                'allocations': [
                    {'symbol': '0050', 'name': '元大台灣50', 'type': 'etf', 'weight': 0.35},
                    {'symbol': '00878', 'name': '國泰永續高股息', 'type': 'etf', 'weight': 0.25},
                    {'symbol': '00679B', 'name': '元大美債20年', 'type': 'bonds', 'weight': 0.30},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.10}
                ]
            },
            'growth': {
                'name': '成長配置',
                'allocations': [
                    {'symbol': '0050', 'name': '元大台灣50', 'type': 'etf', 'weight': 0.35},
                    {'symbol': '2330', 'name': '台積電', 'type': 'stocks', 'weight': 0.30},
                    {'symbol': '00929', 'name': '復華台灣科技優息', 'type': 'etf', 'weight': 0.25},
                    {'symbol': 'CASH', 'name': '現金', 'type': 'cash', 'weight': 0.10}
                ]
            }
        }
        
        selected = profiles.get(profile, profiles['balanced'])
        
        return {
            'total_amount': amount,
            'profile': profile,
            'profile_name': selected['name'],
            'allocations': [
                {
                    **item,
                    'weight_percent': f"{item['weight']*100:.0f}%",
                    'amount': round(amount * item['weight'], 0)
                }
                for item in selected['allocations']
            ]
        }
    
    # ==========================================
    # 轉換為字典（供 API 回傳）
    # ==========================================
    def to_dict(self, result: AllocationResult) -> Dict:
        """將結果轉換為字典格式"""
        return {
            'total_amount': result.total_amount,
            'risk_level': result.risk_level,
            'risk_level_name': result.risk_level_name,
            'goal': result.goal,
            'summary': result.summary,
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
                    'expected_yield': a.expected_yield
                }
                for a in result.allocations
            ]
        }


# ============================================
# 建立單例服務
# ============================================
portfolio_advisor = PortfolioAdvisor()