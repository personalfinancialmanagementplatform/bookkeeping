import { useState, useEffect } from 'react';
import { transactionsAPI, suggestionsAPI } from '../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3'];

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [summaryRes, suggestionsRes] = await Promise.all([
        transactionsAPI.getSummary(),
        suggestionsAPI.get()
      ]);
      setSummary(summaryRes.data);
      setSuggestions(suggestionsRes.data.suggestions || []);
    } catch (error) {
      console.error('載入資料失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="card">載入中...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: '30px', color: '#2c3e50' }}>📊 財務總覽</h1>
      
      {/* 統計卡片 */}
      <div className="stats-grid">
        <div className="stat-card income">
          <h4>💰 本月收入</h4>
          <div className="amount">
            ${summary?.total_income?.toLocaleString() || 0}
          </div>
        </div>
        <div className="stat-card expense">
          <h4>💸 本月支出</h4>
          <div className="amount">
            ${summary?.total_expense?.toLocaleString() || 0}
          </div>
        </div>
        <div className="stat-card balance">
          <h4>📈 本月結餘</h4>
          <div className="amount">
            ${summary?.net?.toLocaleString() || 0}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* 支出分類圖表 */}
        <div className="card">
          <h3>📊 支出分類</h3>
          {summary?.categories_breakdown?.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={summary.categories_breakdown}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ category, amount }) => `${category}: $${amount}`}
                >
                  {summary.categories_breakdown.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: '#999', textAlign: 'center', padding: '50px' }}>
              尚無支出資料
            </p>
          )}
        </div>

        {/* 智慧建議 */}
        <div className="card">
          <h3>💡 智慧建議</h3>
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