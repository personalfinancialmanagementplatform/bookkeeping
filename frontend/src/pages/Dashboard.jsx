import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { transactionsAPI, suggestionsAPI, goalsAPI } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA', '#FFD93D'];

// 資產類型顏色
const ASSET_COLORS = {
  stock: '#e74c3c',
  etf: '#3498db',
  bond: '#27ae60',
  fund: '#f39c12',
  other: '#95a5a6'
};

function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [goals, setGoals] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [summaryRes, suggestionsRes, goalsRes] = await Promise.all([
        transactionsAPI.getSummary(),
        suggestionsAPI.get(),
        goalsAPI.getAll()
      ]);
      setSummary(summaryRes.data);
      setSuggestions(suggestionsRes.data.suggestions || []);
      setGoals(goalsRes.data.filter(g => g.status === 'in_progress'));
      
      // 載入投資組合摘要
      await loadPortfolio();
    } catch (error) {
      console.error('載入資料失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolio = async () => {
    try {
      const response = await fetch('http://localhost:5005/api/portfolio/summary');
      if (response.ok) {
        const data = await response.json();
        setPortfolio(data);
      }
    } catch (error) {
      console.error('載入投資組合失敗:', error);
    }
  };

  if (loading) {
    return <div className="card">載入中...</div>;
  }

  // 計算結餘的正負符號和顏色
  const netAmount = summary?.net || 0;
  const netSign = netAmount >= 0 ? '+' : '';
  const netColor = netAmount >= 0 ? '#27ae60' : '#e74c3c';

  // 計算投資組合最大市值（用於長條圖比例）
  const maxMarketValue = portfolio?.holdings?.length > 0 
    ? Math.max(...portfolio.holdings.map(h => h.market_value || 0))
    : 0;

  return (
    <div>
      <h1 style={{ marginBottom: '30px', color: '#2c3e50' }}>📊 財務總覽</h1>
      
      {/* 統計卡片 */}
      <div className="stats-grid">
        <div className="stat-card income">
          <h4>💰 本月收入</h4>
          <div className="amount">
            +${summary?.total_income?.toLocaleString() || 0}
          </div>
        </div>
        <div className="stat-card expense">
          <h4>💸 本月支出</h4>
          <div className="amount">
            -${summary?.total_expense?.toLocaleString() || 0}
          </div>
        </div>
        <div className="stat-card balance">
          <h4>📈 本月結餘</h4>
          <div className="amount" style={{ color: netColor }}>
            {netSign}${Math.abs(netAmount).toLocaleString()}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* 支出分類圖表 */}
        <div className="card">
          <h3>📊 支出分類</h3>
          {summary?.categories_breakdown?.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={summary.categories_breakdown}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                  >
                    {summary.categories_breakdown.map((entry, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
              
              {/* 類別列表 */}
              <div style={{ marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
                {summary.categories_breakdown.map((item, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '8px 0',
                    borderBottom: '1px solid #f5f5f5'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        width: '12px',
                        height: '12px',
                        borderRadius: '50%',
                        backgroundColor: COLORS[index % COLORS.length]
                      }} />
                      <span>{item.icon} {item.category}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                      <span style={{ color: '#666' }}>
                        {((item.amount / summary.total_expense) * 100).toFixed(1)}%
                      </span>
                      <span style={{ fontWeight: 'bold', color: '#e74c3c' }}>
                        ${item.amount.toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p style={{ color: '#999', textAlign: 'center', padding: '50px' }}>
              尚無支出資料
            </p>
          )}
        </div>

        {/* 智慧建議 + 目標進度 */}
        <div className="card">
          <h3>💡 智慧建議</h3>
          
          {/* 目標進度區塊 */}
          {goals.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '0.95rem', color: '#666', marginBottom: '10px' }}>
                🎯 目標進度
              </h4>
              {goals.slice(0, 3).map((goal, index) => (
                <div key={index} style={{ 
                  background: '#f8f9fa', 
                  borderRadius: '8px', 
                  padding: '12px',
                  marginBottom: '10px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span style={{ fontWeight: '500' }}>{goal.name}</span>
                    <span style={{ color: '#3498db', fontWeight: 'bold' }}>
                      {goal.progress?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="progress-bar" style={{ height: '6px' }}>
                    <div 
                      className="progress"
                      style={{ 
                        width: `${Math.min(goal.progress, 100)}%`,
                        background: goal.progress >= 100 ? '#27ae60' : '#3498db'
                      }}
                    />
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#999', marginTop: '5px' }}>
                    ${goal.current_amount?.toLocaleString()} / ${goal.target_amount?.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 建議列表 */}
          {suggestions.length > 0 ? (
            suggestions.map((s, index) => (
              <div key={index} className={`suggestion-card ${s.type}`}>
                <div className="category">{s.category}</div>
                <div>{s.message}</div>
              </div>
            ))
          ) : (
            <p style={{ color: '#999' }}>目前沒有建議</p>
          )}
        </div>
      </div>

      {/* 投資組合概覽 */}
      {portfolio && portfolio.holdings?.length > 0 && (
        <div className="card" style={{ marginTop: '20px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ margin: 0 }}>📈 投資組合概覽</h3>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.85rem', color: '#666' }}>總市值</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2c3e50' }}>
                NT$ {portfolio.total_value?.toLocaleString()}
              </div>
            </div>
          </div>

          {/* 持倉長條圖列表 */}
          <div style={{ marginBottom: '20px' }}>
            {portfolio.holdings
              .sort((a, b) => (b.market_value || 0) - (a.market_value || 0))
              .slice(0, 5)
              .map((holding, index) => {
                const profit = holding.profit || 0;
                const profitColor = profit >= 0 ? '#27ae60' : '#e74c3c';
                const profitSign = profit >= 0 ? '+' : '';
                const barWidth = maxMarketValue > 0 
                  ? ((holding.market_value || 0) / maxMarketValue) * 100 
                  : 0;
                const assetColor = ASSET_COLORS[holding.asset_type] || ASSET_COLORS.other;

                return (
                  <div key={index} style={{ marginBottom: '16px' }}>
                    {/* 標的資訊 */}
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '6px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{
                          display: 'inline-block',
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: assetColor
                        }} />
                        <span style={{ fontWeight: '600', color: '#2c3e50' }}>
                          {holding.symbol}
                        </span>
                        <span style={{ color: '#666', fontSize: '0.9rem' }}>
                          {holding.name}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                        <span style={{ fontWeight: '500' }}>
                          NT$ {holding.market_value?.toLocaleString()}
                        </span>
                        <span style={{ 
                          fontWeight: '600', 
                          color: profitColor,
                          minWidth: '100px',
                          textAlign: 'right'
                        }}>
                          {profitSign}NT$ {Math.abs(profit).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* 長條圖 */}
                    <div style={{
                      width: '100%',
                      height: '12px',
                      backgroundColor: '#f0f0f0',
                      borderRadius: '6px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${barWidth}%`,
                        height: '100%',
                        backgroundColor: assetColor,
                        borderRadius: '6px',
                        transition: 'width 0.5s ease'
                      }} />
                    </div>
                  </div>
                );
              })}
          </div>

          {/* 總損益 & 查看更多 */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingTop: '15px',
            borderTop: '1px solid #eee'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <span style={{ color: '#666' }}>總損益</span>
              <span style={{
                fontSize: '1.2rem',
                fontWeight: 'bold',
                color: (portfolio.total_profit || 0) >= 0 ? '#27ae60' : '#e74c3c'
              }}>
                {(portfolio.total_profit || 0) >= 0 ? '+' : ''}
                NT$ {Math.abs(portfolio.total_profit || 0).toLocaleString()}
                <span style={{ fontSize: '0.9rem', marginLeft: '8px' }}>
                  ({portfolio.total_profit_rate || '0.00'}%)
                </span>
              </span>
            </div>
            <button
              onClick={() => navigate('/portfolio')}
              style={{
                background: 'none',
                border: '1px solid #3498db',
                color: '#3498db',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                e.target.style.background = '#3498db';
                e.target.style.color = 'white';
              }}
              onMouseOut={(e) => {
                e.target.style.background = 'none';
                e.target.style.color = '#3498db';
              }}
            >
              查看完整持倉 →
            </button>
          </div>

          {/* 如果有超過5筆，顯示提示 */}
          {portfolio.holdings.length > 5 && (
            <div style={{ 
              textAlign: 'center', 
              color: '#999', 
              fontSize: '0.85rem',
              marginTop: '10px'
            }}>
              還有 {portfolio.holdings.length - 5} 檔持倉未顯示
            </div>
          )}
        </div>
      )}

      {/* 沒有投資組合時顯示 */}
      {(!portfolio || portfolio.holdings?.length === 0) && (
        <div className="card" style={{ marginTop: '20px', textAlign: 'center', padding: '40px' }}>
          <h3>📈 投資組合概覽</h3>
          <p style={{ color: '#999', margin: '20px 0' }}>尚無投資持倉</p>
          <button
            onClick={() => navigate('/portfolio')}
            style={{
              background: '#3498db',
              color: 'white',
              border: 'none',
              padding: '10px 24px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.95rem'
            }}
          >
            前往新增持倉 →
          </button>
        </div>
      )}
    </div>
  );
}

export default Dashboard;