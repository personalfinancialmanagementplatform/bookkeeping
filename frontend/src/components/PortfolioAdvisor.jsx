/**
 * 投資組合配置建議組件
 * 檔案位置: frontend/src/components/PortfolioAdvisor.jsx
 */

import React, { useState } from 'react';
import RiskQuestionnaire from './RiskQuestionnaire';
import { usePortfolioRecommendation } from '../hooks/useStockData';
import './PortfolioAdvisor.css';

const RISK_OPTIONS = [
  {
    value: 'conservative',
    name: '保守型',
    icon: '🛡️',
    description: '追求穩定收益，降低波動',
    color: '#27ae60'
  },
  {
    value: 'moderate',
    name: '穩健型',
    icon: '⚖️',
    description: '平衡成長與風險',
    color: '#3498db'
  },
  {
    value: 'aggressive',
    name: '積極型',
    icon: '🚀',
    description: '追求較高資本成長',
    color: '#e67e22'
  }
];

const GOAL_OPTIONS = [
  { value: 'retirement', name: '退休規劃', icon: '🏖️' },
  { value: 'wealth_growth', name: '財富增長', icon: '📈' },
  { value: 'income', name: '穩定收益', icon: '💰' },
  { value: 'preservation', name: '資產保值', icon: '🔒' }
];

const ASSET_COLORS = {
  stocks: '#e74c3c',
  etf: '#3498db',
  bonds: '#2ecc71',
  cash: '#95a5a6'
};

const ASSET_LABELS = {
  stocks: '股票',
  etf: 'ETF',
  bonds: '債券',
  cash: '現金'
};

const PortfolioAdvisor = ({ existingHoldings = [], onApply, onClose }) => {
  const [step, setStep] = useState('input'); // 'questionnaire', 'input', 'result'
  const [amount, setAmount] = useState(100000);
  const [riskLevel, setRiskLevel] = useState('moderate');
  const [goal, setGoal] = useState('wealth_growth');
  const [age, setAge] = useState('');
  
  const { 
    recommendation, 
    loading, 
    error, 
    getRecommendation,
    getQuickRecommendation,
    clear 
  } = usePortfolioRecommendation();

  const handleQuestionnaireComplete = (resultRiskLevel) => {
    setRiskLevel(resultRiskLevel);
    setStep('input');
  };

  const handleSkipQuestionnaire = () => {
    setStep('input');
  };

  const handleStartQuestionnaire = () => {
    setStep('questionnaire');
  };

  const handleGetRecommendation = async () => {
    await getRecommendation({
      amount,
      risk_level: riskLevel,
      goal,
      age: age ? parseInt(age) : null,
      existing_holdings: existingHoldings
    });
    setStep('result');
  };

  const handleQuickRecommendation = async (profile) => {
    await getQuickRecommendation(amount, profile);
    setStep('result');
  };

  const handleReconfigure = () => {
    clear();
    setStep('input');
  };

  const handleApply = () => {
    if (onApply && recommendation) {
      onApply(recommendation.allocations);
    }
  };

  const formatAmount = (value) => {
    return `NT$ ${Math.round(value).toLocaleString()}`;
  };

  // 計算配置圓餅圖資料
  const getPieData = () => {
    if (!recommendation?.allocations) return [];
    
    const grouped = recommendation.allocations.reduce((acc, a) => {
      const type = a.asset_type || a.type || 'other';
      if (!acc[type]) {
        acc[type] = { name: ASSET_LABELS[type] || type, value: 0, color: ASSET_COLORS[type] || '#999' };
      }
      acc[type].value += a.amount;
      return acc;
    }, {});

    return Object.values(grouped);
  };

  return (
    <div className="portfolio-advisor">
      {onClose && (
        <button className="close-btn" onClick={onClose}>×</button>
      )}

      {/* 步驟 1: 風險問卷 */}
      {step === 'questionnaire' && (
        <RiskQuestionnaire
          onComplete={handleQuestionnaireComplete}
          onSkip={handleSkipQuestionnaire}
        />
      )}

      {/* 步驟 2: 輸入配置參數 */}
      {step === 'input' && (
        <div className="input-container">
          <div className="advisor-header">
            <h2> 投資組合配置建議</h2>
            <p className="subtitle">
              輸入您的投資條件，獲得個人化的資產配置建議
            </p>
          </div>

          {/* 投資金額 */}
          <div className="form-section">
            <label className="form-label">投資金額 (NT$)</label>
            <div className="amount-input-group">
              <input
                type="number"
                className="form-input amount-input"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                min="10000"
                step="10000"
              />
              <div className="amount-presets">
                {[50000, 100000, 300000, 500000, 1000000].map(preset => (
                  <button
                    key={preset}
                    className={`preset-btn ${amount === preset ? 'active' : ''}`}
                    onClick={() => setAmount(preset)}
                  >
                    {preset >= 1000000 ? `${preset/1000000}M` : `${preset/1000}K`}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 風險等級 */}
          <div className="form-section">
            <div className="form-label-row">
              <label className="form-label">風險偏好</label>
              <button 
                className="questionnaire-link"
                onClick={handleStartQuestionnaire}
              >
                風險問卷評估
              </button>
            </div>
            
            <div className="risk-options">
              {RISK_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`risk-option ${riskLevel === option.value ? 'selected' : ''}`}
                  onClick={() => setRiskLevel(option.value)}
                  style={{ '--risk-color': option.color }}
                >
                  <span className="risk-icon">{option.icon}</span>
                  <span className="risk-name">{option.name}</span>
                  <span className="risk-desc">{option.description}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 投資目標 */}
          <div className="form-section">
            <label className="form-label">投資目標</label>
            <div className="goal-options">
              {GOAL_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`goal-option ${goal === option.value ? 'selected' : ''}`}
                  onClick={() => setGoal(option.value)}
                >
                  <span className="goal-icon">{option.icon}</span>
                  <span className="goal-name">{option.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 年齡 */}
          <div className="form-section">
            <label className="form-label">年齡 (選填 用於微調風險建議)</label>
            <input
              type="number"
              className="form-input age-input"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="例如: 35"
              min="18"
              max="100"
            />
          </div>

          {/* 操作按鈕 */}
          <div className="form-actions">
            <button
              className="btn btn-primary btn-lg"
              onClick={handleGetRecommendation}
              disabled={loading || amount < 10000}
            >
              {loading ? '分析中...' : ' 取得配置建議'}
            </button>
          </div>

          {/* 快速配置 */}
          <div className="quick-section">
            <div className="quick-label">或選擇快速配置模板：</div>
            <div className="quick-buttons">
              <button 
                className="quick-btn"
                onClick={() => handleQuickRecommendation('conservative')}
                disabled={loading}
              >
                保守配置
              </button>
              <button 
                className="quick-btn"
                onClick={() => handleQuickRecommendation('balanced')}
                disabled={loading}
              >
                平衡配置
              </button>
              <button 
                className="quick-btn"
                onClick={() => handleQuickRecommendation('growth')}
                disabled={loading}
              >
                成長配置
              </button>
            </div>
          </div>

          {error && (
            <div className="error-message">❌ {error}</div>
          )}
        </div>
      )}

      {/* 步驟 3: 配置結果 */}
      {step === 'result' && recommendation && (
        <div className="result-container">
          <div className="result-header">
            <h2> 您的配置建議</h2>
            <button className="reconfigure-btn" onClick={handleReconfigure}>
              ← 重新配置
            </button>
          </div>

          {/* 摘要卡片 */}
          <div className="summary-card">
            <div className="summary-row">
              <div className="summary-item">
                <span className="summary-label">投資金額</span>
                <span className="summary-value">{formatAmount(recommendation.total_amount)}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">風險等級</span>
                <span className="summary-value">{recommendation.risk_level_name || recommendation.profile_name}</span>
              </div>
              {recommendation.expected_total_yield && (
                <div className="summary-item">
                  <span className="summary-label">預估殖利率</span>
                  <span className="summary-value highlight">{recommendation.expected_total_yield}%</span>
                </div>
              )}
            </div>
            {recommendation.summary && (
              <div className="summary-text">{recommendation.summary}</div>
            )}
          </div>

          {/* 配置圖表 */}
          <div className="chart-section">
            <h3>資產配置比例</h3>
            <div className="simple-pie-chart">
              {getPieData().map((item, index) => (
                <div key={index} className="pie-legend-item">
                  <span className="pie-color" style={{ background: item.color }}></span>
                  <span className="pie-name">{item.name}</span>
                  <span className="pie-value">{formatAmount(item.value)}</span>
                  <span className="pie-percent">
                    ({((item.value / recommendation.total_amount) * 100).toFixed(1)}%)
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 配置明細 */}
          <div className="allocations-section">
            <h3>建議標的</h3>
            <div className="allocations-list">
              {recommendation.allocations.map((item, index) => (
                <div key={index} className="allocation-card">
                  <div className="allocation-header">
                    <span 
                      className="type-badge" 
                      style={{ background: ASSET_COLORS[item.asset_type || item.type] || '#999' }}
                    >
                      {ASSET_LABELS[item.asset_type || item.type] || item.asset_type || item.type}
                    </span>
                    <span className="weight">{item.weight_percent}</span>
                  </div>
                  
                  <div className="allocation-body">
                    <div className="symbol">{item.symbol}</div>
                    <div className="name">{item.name}</div>
                    <div className="amount">{formatAmount(item.amount)}</div>
                  </div>
                  
                  {item.reason && (
                    <div className="allocation-reason">{item.reason}</div>
                  )}
                  
                  {item.expected_yield && (
                    <div className="expected-yield">
                      預估殖利率: <strong>{item.expected_yield}%</strong>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 警示 */}
          {recommendation.warnings && recommendation.warnings.length > 0 && (
            <div className="warnings-section">
              <h4>⚠️ 注意事項</h4>
              <ul>
                {recommendation.warnings.map((warning, index) => (
                  <li key={index}>{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 操作按鈕 */}
          <div className="result-actions">
            <button className="btn btn-secondary" onClick={handleReconfigure}>
              重新配置
            </button>
            {onApply && (
              <button className="btn btn-primary" onClick={handleApply}>
                 套用此配置
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioAdvisor;