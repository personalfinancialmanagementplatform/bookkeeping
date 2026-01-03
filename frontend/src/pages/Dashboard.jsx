import { useState, useEffect } from 'react';
import { transactionsAPI, suggestionsAPI, goalsAPI } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA', '#FFD93D'];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [goals, setGoals] = useState([]);
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
    } catch (error) {
      console.error('載入資料失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="card">載入中...</div>;
  }

  // 計算結餘的正負符號和顏色
  const netAmount = summary?.net || 0;
  const netSign = netAmount >= 0 ? '+' : '';
  const netColor = netAmount >= 0 ? '#27ae60' : '#e74c3c';

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
    </div>
  );
}

export default Dashboard;