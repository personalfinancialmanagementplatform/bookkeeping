import { useState, useEffect } from 'react';
import './TechnicalSignals.css';

const API_BASE = 'http://localhost:5005/api';

function TechnicalSignals({ holdings = [], onRefresh }) {
  const [signals, setSignals] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadSignals();
  }, [holdings]);

  const loadSignals = async () => {
    if (!holdings || holdings.length === 0) {
      setSignals([]);
      setSummary(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/technical/signals`);
      
      if (!res.ok) {
        throw new Error('無法取得技術訊號');
      }
      
      const data = await res.json();
      
      setSignals(data.signals || []);
      setSummary(data.summary || null);
      setLastUpdated(new Date().toLocaleTimeString('zh-TW'));
      
    } catch (err) {
      console.error('載入技術訊號失敗:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signalType) => {
    if (signalType === 'golden_cross') return '📈';
    if (signalType === 'death_cross') return '📉';
    return '📊';
  };

  const getSignalColor = (recommendation) => {
    if (recommendation === '買入') return 'buy';
    if (recommendation === '賣出') return 'sell';
    return 'neutral';
  };

  const getStrengthLabel = (strength) => {
    if (strength === 'strong') return '強';
    if (strength === 'weak') return '弱';
    return '普';
  };

  const getIndicatorBadge = (indicator) => {
    if (indicator === 'KD') return { label: 'KD', className: 'badge-kd' };
    if (indicator === 'MA') return { label: 'MA', className: 'badge-ma' };
    return { label: indicator, className: 'badge-other' };
  };

  const displaySignals = expanded ? signals : signals.slice(0, 3);
  const hasMoreSignals = signals.length > 3;

  if (loading) {
    return (
      <div className="card signals-card">
        <h3>🎯 今日技術訊號</h3>
        <div className="signals-loading">
          <div className="loading-spinner"></div>
          <span>分析中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card signals-card">
      <div className="signals-header">
        <h3>🎯 今日技術訊號</h3>
        <button className="btn-refresh" onClick={loadSignals} title="重新分析">
          🔄
        </button>
      </div>

      {error ? (
        <div className="signals-error">
          <span>⚠️ {error}</span>
          <button onClick={loadSignals}>重試</button>
        </div>
      ) : signals.length === 0 ? (
        <div className="signals-empty">
          <div className="empty-icon">✨</div>
          <p>目前持倉無交叉訊號</p>
          <small>系統會持續監控 KD 和均線變化</small>
        </div>
      ) : (
        <>
          {summary && (
            <div className="signals-summary">
              <div className="summary-item buy">
                <span className="count">{summary.buy_signals}</span>
                <span className="label">買入訊號</span>
              </div>
              <div className="summary-item sell">
                <span className="count">{summary.sell_signals}</span>
                <span className="label">賣出訊號</span>
              </div>
              <div className="summary-item total">
                <span className="count">{summary.total_analyzed}</span>
                <span className="label">已分析</span>
              </div>
            </div>
          )}

          <ul className="signals-list">
            {displaySignals.map((signal, index) => {
              const badge = getIndicatorBadge(signal.indicator);
              return (
                <li 
                  key={`${signal.symbol}-${signal.indicator}-${index}`} 
                  className={`signal-item ${getSignalColor(signal.recommendation)}`}
                >
                  <div className="signal-left">
                    <span className="signal-icon">{getSignalIcon(signal.signal_type)}</span>
                    <div className="signal-info">
                      <div className="signal-stock">
                        <strong>{signal.symbol}</strong>
                        <span className="stock-name">{signal.name}</span>
                      </div>
                      <div className="signal-tags">
                        <span className={`indicator-badge ${badge.className}`}>
                          {badge.label}
                        </span>
                        <span className={`strength-badge ${signal.signal_strength}`}>
                          {getStrengthLabel(signal.signal_strength)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="signal-right">
                    <span className={`recommendation ${getSignalColor(signal.recommendation)}`}>
                      {signal.recommendation}
                    </span>
                    <span className="signal-desc" title={signal.description}>
                      {signal.signal_type === 'golden_cross' ? '黃金交叉' : '死亡交叉'}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>

          {hasMoreSignals && (
            <button className="btn-expand" onClick={() => setExpanded(!expanded)}>
              {expanded ? '收起' : `顯示全部 (${signals.length})`}
            </button>
          )}

          {lastUpdated && (
            <div className="signals-footer">
              <small>更新時間：{lastUpdated}</small>
            </div>
          )}
        </>
      )}

      <div className="signals-legend">
        <div className="legend-item">
          <span className="legend-icon golden">📈</span>
          <span>黃金交叉（買入）</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon death">📉</span>
          <span>死亡交叉（賣出）</span>
        </div>
      </div>
    </div>
  );
}

export default TechnicalSignals;