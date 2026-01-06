/**
 * 投資組合配置建議組件
 * 功能：風險問卷評估、配置建議、標的介紹、下單指引、券商比較
 */

import React, { useState } from 'react';
import RiskQuestionnaire from './RiskQuestionnaire';
import './PortfolioAdvisor.css';

const API_BASE = 'http://localhost:5005/api';

// 標的詳細介紹資料庫
const ASSET_DETAILS = {
  // ETF
  '0050': {
    fullName: '元大台灣卓越50證券投資信託基金',
    description: '追蹤台灣50指數，涵蓋台灣市值最大的50家上市公司，包括台積電、鴻海、聯發科等龍頭企業。適合想要分散投資台灣大型股的投資人。',
    features: ['被動式管理', '低管理費(0.43%)', '季配息', '流動性佳'],
    riskLevel: 'RR4',
    minInvestment: '1股約150-160元'
  },
  '0056': {
    fullName: '元大台灣高股息證券投資信託基金',
    description: '精選台灣高殖利率股票，成分股每年調整，著重股息收益。適合追求穩定現金流的投資人。',
    features: ['高股息策略', '年配息', '殖利率約5-6%', '成分股定期調整'],
    riskLevel: 'RR4',
    minInvestment: '1股約35-40元'
  },
  '006208': {
    fullName: '富邦台灣采吉50基金',
    description: '同樣追蹤台灣50指數，管理費比0050更低，適合長期定期定額投資。',
    features: ['超低管理費(0.15%)', '追蹤台灣50指數', '半年配息'],
    riskLevel: 'RR4',
    minInvestment: '1股約85-95元'
  },
  '00878': {
    fullName: '國泰永續高股息ETF',
    description: '結合ESG永續投資與高股息策略，篩選符合環境、社會、公司治理標準的高殖利率股票。',
    features: ['ESG永續篩選', '季配息', '殖利率約5%', '近年最熱門ETF之一'],
    riskLevel: 'RR4',
    minInvestment: '1股約20-25元'
  },
  '00713': {
    fullName: '元大台灣高息低波ETF',
    description: '同時追求高股息與低波動，適合保守型投資人。選股兼顧殖利率與股價穩定性。',
    features: ['低波動策略', '高股息', '季配息', '適合退休族'],
    riskLevel: 'RR3',
    minInvestment: '1股約50-55元'
  },
  '00919': {
    fullName: '群益台灣精選高息ETF',
    description: '月月配息的高股息ETF，提供穩定現金流。殖利率在同類型中名列前茅。',
    features: ['月配息', '高殖利率(8%+)', '精選高息股'],
    riskLevel: 'RR4',
    minInvestment: '1股約25-30元'
  },
  '00929': {
    fullName: '復華台灣科技優息ETF',
    description: '聚焦台灣科技股的月配息ETF，兼顧成長性與配息收益。',
    features: ['科技股為主', '月配息', '成長+配息雙軌'],
    riskLevel: 'RR4',
    minInvestment: '1股約20-22元'
  },
  // 債券ETF
  '00679B': {
    fullName: '元大美債20年ETF',
    description: '投資美國20年期以上公債，與股市相關性低，適合作為資產配置中的避險部位。',
    features: ['美國公債', '避險工具', '與股市負相關', '季配息'],
    riskLevel: 'RR2',
    minInvestment: '1股約30-35元'
  },
  '00687B': {
    fullName: '國泰20年美債ETF',
    description: '追蹤美國20年期公債指數，提供穩定債息收入，適合保守型投資人。',
    features: ['美國長天期公債', '低波動', '季配息'],
    riskLevel: 'RR2',
    minInvestment: '1股約32-38元'
  },
  '00720B': {
    fullName: '元大投資級公司債ETF',
    description: '投資投資等級的公司債券，收益率比公債高，風險適中。',
    features: ['投資級公司債', '收益較公債高', '信用風險低'],
    riskLevel: 'RR3',
    minInvestment: '1股約35-40元'
  },
  '00751B': {
    fullName: '元大AAA至A公司債ETF',
    description: '僅投資最高信評(AAA至A級)的公司債，安全性極高。',
    features: ['最高信評公司債', '安全性高', '適合保守投資'],
    riskLevel: 'RR2',
    minInvestment: '1股約38-42元'
  },
  // 個股
  '2330': {
    fullName: '台灣積體電路製造股份有限公司',
    description: '全球最大晶圓代工廠，技術領先，客戶包括蘋果、輝達等國際大廠。台灣最具代表性的科技股。',
    features: ['全球晶圓代工龍頭', '先進製程領先', '穩定配息', '長期成長潛力'],
    riskLevel: 'RR4',
    minInvestment: '1股約1000-1100元'
  },
  '2317': {
    fullName: '鴻海精密工業股份有限公司',
    description: '全球最大電子代工廠(EMS)，近年積極轉型電動車、AI伺服器等新領域。',
    features: ['全球EMS龍頭', '轉型電動車', 'AI伺服器題材', '穩定配息'],
    riskLevel: 'RR4',
    minInvestment: '1股約180-200元'
  },
  '2454': {
    fullName: '聯發科技股份有限公司',
    description: '台灣IC設計龍頭，主要產品包括手機晶片、智慧家庭、車用晶片等。受惠AI發展趨勢。',
    features: ['IC設計龍頭', 'AI晶片題材', '5G受惠股', '高殖利率'],
    riskLevel: 'RR5',
    minInvestment: '1股約1200-1400元'
  },
  '2382': {
    fullName: '廣達電腦股份有限公司',
    description: 'AI伺服器代工大廠，為輝達、微軟等大廠代工，受惠AI趨勢明顯。',
    features: ['AI伺服器代工', '輝達合作夥伴', '雲端運算受惠', '成長性高'],
    riskLevel: 'RR5',
    minInvestment: '1股約280-320元'
  },
  '2881': {
    fullName: '富邦金融控股股份有限公司',
    description: '台灣最大民營金控，旗下有富邦人壽、台北富邦銀行等，業務多元穩健。',
    features: ['金控龍頭', '穩定配息', '多元金融服務', '防禦性標的'],
    riskLevel: 'RR3',
    minInvestment: '1股約70-80元'
  },
  '2882': {
    fullName: '國泰金融控股股份有限公司',
    description: '台灣最大壽險公司國泰人壽的母公司，長期穩健經營，配息穩定。',
    features: ['壽險龍頭', '穩定配息', '長期投資首選', '防禦性佳'],
    riskLevel: 'RR3',
    minInvestment: '1股約45-55元'
  },
  '2886': {
    fullName: '兆豐金融控股股份有限公司',
    description: '官股金控代表，經營穩健，配息穩定，適合保守型投資人。',
    features: ['官股金控', '穩定配息', '經營穩健', '防禦性佳'],
    riskLevel: 'RR3',
    minInvestment: '1股約40-45元'
  },
  '1216': {
    fullName: '統一企業股份有限公司',
    description: '台灣食品業龍頭，旗下有7-11、統一超商等，民生消費股代表。',
    features: ['食品業龍頭', '民生必需品', '防禦性極佳', '穩定配息'],
    riskLevel: 'RR3',
    minInvestment: '1股約70-80元'
  },
  // 現金
  'CASH': {
    fullName: '現金或貨幣市場基金',
    description: '保持資金流動性，可用於緊急預備金或等待更好的投資機會。',
    features: ['高流動性', '零風險', '隨時可用'],
    riskLevel: 'RR1',
    minInvestment: '不限'
  }
};

// 券商比較資料
const BROKER_COMPARISON = [
  {
    name: '元大證券',
    logo: '🏦',
    discount: '電子下單 6 折',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 有',
    app: '投資先生',
    appRating: '4.5',
    features: ['市佔率第一', '研究報告完整', '據點最多'],
    openAccountUrl: 'https://www.yuanta.com.tw/',
    recommended: true
  },
  {
    name: '富邦證券',
    logo: '🏛️',
    discount: '電子下單 6 折',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 有',
    app: '富邦e點通',
    appRating: '4.3',
    features: ['富邦金控整合', '介面友善', 'LINE 綁定'],
    openAccountUrl: 'https://www.fubon-ebroker.com/',
    recommended: false
  },
  {
    name: '國泰證券',
    logo: '🌳',
    discount: '電子下單 6 折起',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 有',
    app: 'CUBE App',
    appRating: '4.4',
    features: ['樹精靈智能選股', 'CUBE整合', '小資族友善'],
    openAccountUrl: 'https://www.cathaysec.com.tw/',
    recommended: false
  },
  {
    name: '永豐金證券',
    logo: '💎',
    discount: '電子下單 65 折',
    effectiveFee: '0.0926%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 豐存股',
    app: '大戶投',
    appRating: '4.6',
    features: ['介面現代化', '豐存股功能強', '手續費低'],
    openAccountUrl: 'https://www.sinotrade.com.tw/',
    recommended: true
  },
  {
    name: '玉山證券',
    logo: '🗻',
    discount: '電子下單 6 折',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有（富果）',
    regularInvest: '✅ 有',
    app: '玉山證券 / 富果',
    appRating: '4.5',
    features: ['富果帳戶', '新手友善', '介面美觀'],
    openAccountUrl: 'https://www.fugle.tw/',
    recommended: true
  },
  {
    name: '中國信託證券',
    logo: '🔵',
    discount: '電子下單 6 折',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 有',
    app: '亮點App',
    appRating: '4.2',
    features: ['中信金整合', '信用卡優惠', '據點多'],
    openAccountUrl: 'https://www.win168.com.tw/',
    recommended: false
  },
  {
    name: '凱基證券',
    logo: '🟢',
    discount: '電子下單 6 折',
    effectiveFee: '0.0855%',
    minFee: '20 元',
    fractionalShare: '✅ 有',
    regularInvest: '✅ 定期定股',
    app: '隨身營業員',
    appRating: '4.1',
    features: ['定期定股', '研究資源豐富', '法人服務'],
    openAccountUrl: 'https://www.kgieworld.com.tw/',
    recommended: false
  },
  {
    name: '新光證券',
    logo: '🟡',
    discount: '電子下單 28 折',
    effectiveFee: '0.0399%',
    minFee: '20 元',
    fractionalShare: '❌ 無',
    regularInvest: '✅ 有',
    app: '新光證券',
    appRating: '3.8',
    features: ['手續費超低', '新戶優惠多', '適合大戶'],
    openAccountUrl: 'https://www.skis.com.tw/',
    recommended: false
  },
];

// 熱門標的快速選擇（用於自訂標的）
const POPULAR_ASSETS = [
  { symbol: '0050', name: '元大台灣50', type: 'etf' },
  { symbol: '0056', name: '元大高股息', type: 'etf' },
  { symbol: '00878', name: '國泰永續高股息', type: 'etf' },
  { symbol: '00919', name: '群益台灣精選高息', type: 'etf' },
  { symbol: '00929', name: '復華台灣科技優息', type: 'etf' },
  { symbol: '006208', name: '富邦台50', type: 'etf' },
  { symbol: '2330', name: '台積電', type: 'stock' },
  { symbol: '2317', name: '鴻海', type: 'stock' },
  { symbol: '2454', name: '聯發科', type: 'stock' },
  { symbol: '2382', name: '廣達', type: 'stock' },
  { symbol: '2881', name: '富邦金', type: 'stock' },
  { symbol: '2882', name: '國泰金', type: 'stock' },
  { symbol: '00679B', name: '元大美債20年', type: 'bond' },
  { symbol: '00687B', name: '國泰20年美債', type: 'bond' },
];

const PortfolioAdvisor = ({ existingHoldings = [], onApply, onClose }) => {
  // 狀態管理
  const [step, setStep] = useState('method');
  const [riskLevel, setRiskLevel] = useState('moderate');
  const [investmentGoal, setInvestmentGoal] = useState('wealth_growth');
  const [amount, setAmount] = useState(10000);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedAsset, setExpandedAsset] = useState(null);
  const [showBrokerComparison, setShowBrokerComparison] = useState(false);
  
  // 自訂投資標的相關狀態
  const [customAssets, setCustomAssets] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [age, setAge] = useState('');

  // 風險等級選項
  const riskOptions = [
    { value: 'conservative', label: '🛡️ 保守型', desc: '追求穩定收益，降低波動' },
    { value: 'moderate', label: '⚖️ 穩健型', desc: '平衡成長與風險' },
    { value: 'aggressive', label: '🚀 積極型', desc: '追求較高資本成長' }
  ];

  // 投資目標選項
  const goalOptions = [
    { value: 'retirement', label: '🏖️ 退休規劃', desc: '長期穩定增長' },
    { value: 'wealth_growth', label: '📈 財富增長', desc: '追求資本增值' },
    { value: 'income', label: '💰 穩定收益', desc: '股息現金流' },
    { value: 'preservation', label: '🔒 資產保值', desc: '抵抗通膨' }
  ];

  // 搜尋標的
  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.length < 1) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }

    // 先從本地熱門標的搜尋
    const localResults = POPULAR_ASSETS.filter(
      asset => asset.symbol.includes(query.toUpperCase()) || 
               asset.name.includes(query)
    );

    if (localResults.length > 0) {
      setSearchResults(localResults.slice(0, 8));
      setShowSearchDropdown(true);
      return;
    }

    // 如果本地沒有，可以呼叫 API 搜尋
    try {
      const response = await fetch(`${API_BASE}/stocks/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.slice(0, 8));
        setShowSearchDropdown(true);
      }
    } catch {
      setSearchResults(localResults);
      setShowSearchDropdown(localResults.length > 0);
    }
  };

  // 新增自訂標的
  const addCustomAsset = (asset) => {
    if (!customAssets.find(a => a.symbol === asset.symbol)) {
      setCustomAssets([...customAssets, asset]);
    }
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchDropdown(false);
  };

  // 移除自訂標的
  const removeCustomAsset = (symbol) => {
    setCustomAssets(customAssets.filter(a => a.symbol !== symbol));
  };

  // 取得配置建議
  const getRecommendation = async () => {
    if (amount < 1000) {
      setError('最低投資金額為 1,000 元');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/portfolio/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          risk_level: riskLevel,
          goal: investmentGoal,
          existing_holdings: existingHoldings,
          custom_assets: customAssets.map(a => a.symbol),
          age: age ? parseInt(age) : null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '取得建議失敗');
      }

      setRecommendation(data);
      setStep('result');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 問卷完成
  const handleQuestionnaireComplete = (level) => {
    setRiskLevel(level);
    setStep('amount');
  };

  // 手動選擇完成
  const handleManualNext = () => {
    setStep('amount');
  };

  // 重新配置
  const handleReconfigure = () => {
    setStep('method');
    setRecommendation(null);
    setExpandedAsset(null);
  };

  // 套用配置
  const handleApply = () => {
    if (onApply && recommendation) {
      onApply(recommendation);
    }
    if (onClose) {
      onClose();
    }
  };

  // 取得資產類型標籤
  const getAssetTypeLabel = (type) => {
    const labels = {
      'etf': 'ETF',
      'stocks': '股票',
      'stock': '股票',
      'bonds': '債券',
      'bond': '債券',
      'cash': '現金'
    };
    return labels[type] || type;
  };

  // 取得資產類型顏色
  const getAssetTypeColor = (type) => {
    const colors = {
      'etf': '#3498db',
      'stocks': '#e74c3c',
      'stock': '#e74c3c',
      'bonds': '#27ae60',
      'bond': '#27ae60',
      'cash': '#95a5a6'
    };
    return colors[type] || '#666';
  };

  // 渲染步驟 1：選擇評估方式
  const renderMethodStep = () => (
    <div className="advisor-step">
      <h3>📋 選擇風險評估方式</h3>
      <p className="step-desc">我們需要了解您的風險承受能力，以提供適合的配置建議</p>
      
      <div className="method-options">
        <button 
          className="method-card"
          onClick={() => setStep('questionnaire')}
        >
          <span className="method-icon">📝</span>
          <span className="method-title">風險問卷評估</span>
          <span className="method-desc">回答 12 題金管會標準問卷，精準評估風險屬性</span>
          <span className="method-tag recommended">推薦</span>
        </button>
        
        <button 
          className="method-card"
          onClick={() => setStep('manual')}
        >
          <span className="method-icon">🎯</span>
          <span className="method-title">直接選擇偏好</span>
          <span className="method-desc">已了解自己的投資風格，直接選擇風險等級</span>
        </button>
      </div>
    </div>
  );

  // 渲染步驟 2a：問卷評估
  const renderQuestionnaireStep = () => (
    <div className="advisor-step">
      <RiskQuestionnaire 
        onComplete={handleQuestionnaireComplete}
        onSkip={() => setStep('manual')}
      />
    </div>
  );

  // 渲染步驟 2b：手動選擇
  const renderManualStep = () => (
    <div className="advisor-step">
      <h3>🎯 選擇您的投資偏好</h3>
      
      <div className="form-section">
        <label>風險等級</label>
        <div className="option-cards">
          {riskOptions.map(opt => (
            <button
              key={opt.value}
              className={`option-card ${riskLevel === opt.value ? 'selected' : ''}`}
              onClick={() => setRiskLevel(opt.value)}
            >
              <span className="option-label">{opt.label}</span>
              <span className="option-desc">{opt.desc}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="form-section">
        <label>投資目標</label>
        <div className="option-cards">
          {goalOptions.map(opt => (
            <button
              key={opt.value}
              className={`option-card ${investmentGoal === opt.value ? 'selected' : ''}`}
              onClick={() => setInvestmentGoal(opt.value)}
            >
              <span className="option-label">{opt.label}</span>
              <span className="option-desc">{opt.desc}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="step-actions">
        <button className="btn btn-secondary" onClick={() => setStep('method')}>
          ← 返回
        </button>
        <button className="btn btn-primary" onClick={handleManualNext}>
          下一步 →
        </button>
      </div>
    </div>
  );

  // 渲染步驟 3：輸入金額（含自訂標的功能）
  const renderAmountStep = () => (
    <div className="advisor-step">
      <h3>💰 設定投資金額</h3>
      
      <div className="risk-summary">
        <span className="risk-badge" data-level={riskLevel}>
          {riskOptions.find(r => r.value === riskLevel)?.label}
        </span>
        <span className="goal-badge">
          {goalOptions.find(g => g.value === investmentGoal)?.label}
        </span>
      </div>

      <div className="form-section">
        <label>投資金額 (NT$)</label>
        <input
          type="number"
          className="amount-input"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          min="1000"
          step="1000"
          placeholder="輸入投資金額"
        />
        {amount < 1000 && (
          <p className="error-hint">⚠️ 最低投資金額為 1,000 元</p>
        )}
        <p className="amount-display">
          = NT$ {Number(amount).toLocaleString()}
        </p>
      </div>

      {/* 自訂投資標的區塊 */}
      <div className="form-section custom-assets-section">
        <label>自訂投資標的 (選填)</label>
        <p className="section-hint">加入您想要的股票或 ETF，系統將優先納入配置</p>
        
        {/* 搜尋框 */}
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="搜尋股票代號或名稱..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            onFocus={() => searchResults.length > 0 && setShowSearchDropdown(true)}
            onBlur={() => setTimeout(() => setShowSearchDropdown(false), 200)}
          />
          
          {/* 搜尋結果下拉選單 */}
          {showSearchDropdown && searchResults.length > 0 && (
            <div className="search-dropdown">
              {searchResults.map((result) => (
                <div
                  key={result.symbol}
                  className="search-item"
                  onClick={() => addCustomAsset(result)}
                >
                  <span className="search-item-symbol">{result.symbol}</span>
                  <span className="search-item-name">{result.name}</span>
                  <span 
                    className="search-item-type"
                    style={{ backgroundColor: getAssetTypeColor(result.type) }}
                  >
                    {getAssetTypeLabel(result.type)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 熱門標的快速選擇 */}
        <div className="popular-assets">
          <span className="popular-label">熱門：</span>
          {POPULAR_ASSETS.slice(0, 6).map((asset) => (
            <button
              key={asset.symbol}
              className={`popular-tag ${customAssets.find(a => a.symbol === asset.symbol) ? 'selected' : ''}`}
              onClick={() => addCustomAsset(asset)}
              disabled={customAssets.find(a => a.symbol === asset.symbol)}
            >
              {asset.symbol}
            </button>
          ))}
        </div>

        {/* 已選擇的標的 */}
        {customAssets.length > 0 && (
          <div className="selected-assets">
            <span className="selected-label">已選擇：</span>
            <div className="selected-list">
              {customAssets.map((asset) => (
                <span key={asset.symbol} className="selected-tag">
                  <span 
                    className="tag-type-dot"
                    style={{ backgroundColor: getAssetTypeColor(asset.type) }}
                  ></span>
                  {asset.symbol} {asset.name}
                  <button 
                    className="remove-btn"
                    onClick={() => removeCustomAsset(asset.symbol)}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 年齡輸入 */}
      <div className="form-section age-section">
        <label>年齡 (選填，用於微調風險建議)</label>
        <input
          type="number"
          className="age-input"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          min="18"
          max="100"
          placeholder="例如: 35"
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="step-actions">
        <button className="btn btn-secondary" onClick={() => setStep('manual')}>
          ← 返回
        </button>
        <button 
          className="btn btn-primary" 
          onClick={getRecommendation}
          disabled={loading || amount < 1000}
        >
          {loading ? '計算中...' : '🎯 取得配置建議'}
        </button>
      </div>
    </div>
  );

  // 渲染步驟 4：配置結果
  const renderResultStep = () => {
    if (!recommendation) return null;

    return (
      <div className="advisor-step result-step">
        <div className="result-header">
          <h3>📊 投資組合配置建議</h3>
          <p className="result-summary">{recommendation.summary}</p>
        </div>

        {/* 配置概覽 */}
        <div className="result-overview">
          <div className="overview-item">
            <span className="overview-label">投資金額</span>
            <span className="overview-value">NT$ {recommendation.total_amount?.toLocaleString()}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">風險等級</span>
            <span className="overview-value">{recommendation.risk_level_name}</span>
          </div>
          <div className="overview-item">
            <span className="overview-label">預估年化報酬</span>
            <span className="overview-value highlight">{recommendation.expected_total_yield}%</span>
          </div>
        </div>

        {/* 顯示自訂標的是否被納入 */}
        {customAssets.length > 0 && (
          <div className="custom-assets-notice">
            <span className="notice-icon">✨</span>
            <span>已將您選擇的 {customAssets.length} 檔標的優先納入配置</span>
          </div>
        )}

        {/* 資產配置列表 */}
        <div className="allocation-list">
          <h4>📋 建議標的明細（點擊展開詳情）</h4>
          {recommendation.allocations?.map((item, index) => {
            const details = ASSET_DETAILS[item.symbol];
            const isExpanded = expandedAsset === item.symbol;
            const isCustom = customAssets.find(a => a.symbol === item.symbol);
            
            return (
              <div key={index} className={`allocation-item ${isExpanded ? 'expanded' : ''} ${isCustom ? 'is-custom' : ''}`}>
                <div 
                  className="allocation-main"
                  onClick={() => setExpandedAsset(isExpanded ? null : item.symbol)}
                >
                  <div className="allocation-left">
                    <span 
                      className="asset-type-badge"
                      style={{ backgroundColor: getAssetTypeColor(item.asset_type) }}
                    >
                      {getAssetTypeLabel(item.asset_type)}
                    </span>
                    <div className="asset-info">
                      <span className="asset-symbol">
                        {item.symbol}
                        {isCustom && <span className="custom-badge">自選</span>}
                      </span>
                      <span className="asset-name">{item.name}</span>
                    </div>
                  </div>
                  <div className="allocation-right">
                    <span className="allocation-weight">{item.weight_percent}</span>
                    <span className="allocation-amount">NT$ {item.amount?.toLocaleString()}</span>
                    <span className="expand-icon">{isExpanded ? '▲' : '▼'}</span>
                  </div>
                </div>

                {/* 展開的詳細資訊 */}
                {isExpanded && details && (
                  <div className="allocation-details">
                    <div className="detail-section">
                      <h5>📖 標的介紹</h5>
                      <p className="detail-fullname">{details.fullName}</p>
                      <p className="detail-description">{details.description}</p>
                    </div>

                    <div className="detail-section">
                      <h5>✨ 特色</h5>
                      <div className="detail-features">
                        {details.features.map((f, i) => (
                          <span key={i} className="feature-tag">{f}</span>
                        ))}
                      </div>
                    </div>

                    <div className="detail-grid">
                      <div className="detail-row">
                        <span className="detail-label">風險等級</span>
                        <span className={`detail-value rr-badge ${details.riskLevel?.toLowerCase()}`}>
                          {details.riskLevel}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">最低投資</span>
                        <span className="detail-value">{details.minInvestment}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">預估殖利率</span>
                        <span className="detail-value highlight">{item.expected_yield}%</span>
                      </div>
                    </div>

                    <div className="detail-reason">
                      <span className="detail-label">💡 推薦理由</span>
                      <p>{item.reason}</p>
                    </div>
                  </div>
                )}

                {isExpanded && !details && (
                  <div className="allocation-details">
                    <div className="detail-reason">
                      <span className="detail-label">💡 推薦理由</span>
                      <p>{item.reason}</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 下一步操作指引 */}
        <div className="next-steps-section">
          <h4>🚀 下一步：如何開始投資？</h4>
          
          <div className="steps-guide">
            <div className="guide-step">
              <span className="step-number">1</span>
              <div className="step-content">
                <h5>開立證券戶</h5>
                <p>如果您還沒有證券帳戶，請先到券商開戶。建議選擇有定期定額功能的券商。</p>
                <button 
                  className="btn-broker-compare"
                  onClick={() => setShowBrokerComparison(true)}
                >
                  📊 證券戶比較
                </button>
              </div>
            </div>
            <div className="guide-step">
              <span className="step-number">2</span>
              <div className="step-content">
                <h5>入金到交割帳戶</h5>
                <p>將資金轉入綁定的銀行交割帳戶，台股採用 T+2 交割制度。</p>
              </div>
            </div>
            <div className="guide-step">
              <span className="step-number">3</span>
              <div className="step-content">
                <h5>下單買進</h5>
                <p>透過券商 App 或網頁下單。建議使用「定期定額」分批買進。</p>
              </div>
            </div>
            <div className="guide-step">
              <span className="step-number">4</span>
              <div className="step-content">
                <h5>定期檢視與再平衡</h5>
                <p>每季或每半年檢視投資組合，必要時進行再平衡。</p>
              </div>
            </div>
          </div>
        </div>

        {/* 券商比較彈窗 */}
        {showBrokerComparison && (
          <div className="broker-comparison-overlay" onClick={() => setShowBrokerComparison(false)}>
            <div className="broker-comparison-modal" onClick={(e) => e.stopPropagation()}>
              <div className="comparison-header">
                <h3>📊 證券商開戶比較</h3>
                <button className="close-btn" onClick={() => setShowBrokerComparison(false)}>×</button>
              </div>
              
              <div className="comparison-intro">
                <p>📌 台股手續費公定價為成交金額的 <strong>0.1425%</strong>，各券商提供不同電子下單折扣。</p>
                <p>📌 建議選擇有「定期定額」及「零股交易」功能的券商，方便小額投資。</p>
              </div>

              <div className="comparison-table-wrapper">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>券商</th>
                      <th>電子下單折扣</th>
                      <th>實際手續費率</th>
                      <th>最低手續費</th>
                      <th>零股交易</th>
                      <th>定期定額</th>
                      <th>App 評分</th>
                      <th>特色</th>
                      <th>開戶</th>
                    </tr>
                  </thead>
                  <tbody>
                    {BROKER_COMPARISON.map((broker, index) => (
                      <tr key={index} className={broker.recommended ? 'recommended-row' : ''}>
                        <td className="broker-name-cell">
                          <span className="broker-logo">{broker.logo}</span>
                          <span>{broker.name}</span>
                          {broker.recommended && <span className="recommended-badge">推薦</span>}
                        </td>
                        <td>{broker.discount}</td>
                        <td className="fee-cell">{broker.effectiveFee}</td>
                        <td>{broker.minFee}</td>
                        <td>{broker.fractionalShare}</td>
                        <td>{broker.regularInvest}</td>
                        <td>
                          <span className="app-rating">⭐ {broker.appRating}</span>
                          <span className="app-name">{broker.app}</span>
                        </td>
                        <td className="features-cell">
                          {broker.features.map((f, i) => (
                            <span key={i} className="feature-tag-small">{f}</span>
                          ))}
                        </td>
                        <td>
                          <a 
                            href={broker.openAccountUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="open-account-btn"
                          >
                            前往開戶
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="comparison-notes">
                <h5>💡 開戶小提醒</h5>
                <ul>
                  <li>📋 開戶需準備：雙證件（身分證 + 健保卡或駕照）、印章、銀行帳戶</li>
                  <li>🏦 交割帳戶：部分券商可同時開立銀行帳戶，無需另外準備</li>
                  <li>📱 線上開戶：多數券商支援全線上開戶，約 10-15 分鐘完成</li>
                  <li>⏰ 審核時間：約 1-3 個工作天</li>
                  <li>🎁 新戶優惠：開戶前可查詢各券商新戶禮（手續費折扣、禮券等）</li>
                </ul>
              </div>

              <div className="comparison-footer">
                <button 
                  className="btn btn-secondary"
                  onClick={() => setShowBrokerComparison(false)}
                >
                  關閉
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 警示訊息 */}
        {recommendation.warnings?.length > 0 && (
          <div className="warnings-section">
            <h4>⚠️ 投資提醒</h4>
            <ul className="warnings-list">
              {recommendation.warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 操作按鈕 */}
        <div className="result-actions">
          <button className="btn btn-secondary" onClick={handleReconfigure}>
            🔄 重新配置
          </button>
          {onApply && (
            <button className="btn btn-primary" onClick={handleApply}>
              ✅ 套用此配置
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="portfolio-advisor">
      <div className="advisor-header">
        <h2>🎯 智慧投資組合配置</h2>
        {onClose && (
          <button className="close-btn" onClick={onClose}>×</button>
        )}
      </div>

      <div className="advisor-content">
        {step === 'method' && renderMethodStep()}
        {step === 'questionnaire' && renderQuestionnaireStep()}
        {step === 'manual' && renderManualStep()}
        {step === 'amount' && renderAmountStep()}
        {step === 'result' && renderResultStep()}
      </div>
    </div>
  );
};

export default PortfolioAdvisor;