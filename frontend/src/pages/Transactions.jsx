import { useState, useEffect, useMemo } from 'react';
import { transactionsAPI, categoriesAPI, accountsAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts';

// 類別顏色對照
const CATEGORY_COLORS = {
  '食物飲料': '#FF6B6B',
  '交通': '#4ECDC4',
  '購物': '#95E1D3',
  '娛樂': '#F38181',
  '帳單': '#AA96DA',
  '醫療': '#FCBAD3',
  '教育': '#A8D8EA',
  '其他支出': '#FFD93D',
  '生活必需': '#6BCB77',
  '投資支出': '#4D96FF',
  '保險': '#5C7AEA',
};

// 預設顏色（類別沒有對應時使用）
const DEFAULT_COLORS = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA', '#FFD93D'];

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [timeRange, setTimeRange] = useState('month'); // week / month / year
  const [form, setForm] = useState({
    description: '',
    amount: '',
    type: 'expense',
    category_id: '',
    account_id: '',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [transRes, catRes, accRes] = await Promise.all([
        transactionsAPI.getAll(),
        categoriesAPI.getAll(),
        accountsAPI.getAll()
      ]);
      setTransactions(transRes.data);
      setCategories(catRes.data);
      setAccounts(accRes.data);
    } catch (error) {
      console.error('載入失敗:', error);
    }
  };

  // 根據時間範圍篩選交易
  const filteredTransactions = useMemo(() => {
    const now = new Date();
    let startDate;

    switch (timeRange) {
      case 'week':
        startDate = new Date(now);
        startDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
        break;
      case 'year':
        startDate = new Date(now.getFullYear(), 0, 1);
        break;
      default:
        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
    }

    return transactions.filter(t => new Date(t.date) >= startDate);
  }, [transactions, timeRange]);

  // 計算統計數據
  const stats = useMemo(() => {
    const income = filteredTransactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + (t.amount || 0), 0);
    const expense = filteredTransactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + (t.amount || 0), 0);
    return { income, expense, net: income - expense };
  }, [filteredTransactions]);

  // 生成每日支出堆疊圖數據
  const chartData = useMemo(() => {
    const expenseTransactions = filteredTransactions.filter(t => t.type === 'expense');
    
    // 取得所有支出類別
    const expenseCategories = [...new Set(expenseTransactions.map(t => {
      const cat = categories.find(c => c.id === t.category_id);
      return cat?.name || '其他支出';
    }))];

    // 按日期分組
    const dailyData = {};
    expenseTransactions.forEach(t => {
      const date = t.date;
      if (!dailyData[date]) {
        dailyData[date] = { date };
        expenseCategories.forEach(cat => {
          dailyData[date][cat] = 0;
        });
      }
      const catName = categories.find(c => c.id === t.category_id)?.name || '其他支出';
      dailyData[date][catName] += t.amount || 0;
    });

    // 轉換為陣列並排序
    const result = Object.values(dailyData).sort((a, b) => 
      new Date(a.date) - new Date(b.date)
    );

    return { data: result, categories: expenseCategories };
  }, [filteredTransactions, categories]);

  // 取得類別顏色
  const getCategoryColor = (categoryName, index) => {
    return CATEGORY_COLORS[categoryName] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
  };

  // 格式化日期顯示
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  // 時間範圍標籤
  const getTimeRangeLabel = () => {
    switch (timeRange) {
      case 'week': return '本週';
      case 'month': return '本月';
      case 'year': return '今年';
      default: return '本月';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await transactionsAPI.create({
        ...form,
        amount: parseFloat(form.amount),
        account_id: parseInt(form.account_id) || 1
      });
      setShowModal(false);
      setForm({
        description: '',
        amount: '',
        type: 'expense',
        category_id: '',
        account_id: '',
        date: new Date().toISOString().split('T')[0]
      });
      loadData();
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('確定要刪除這筆交易嗎？')) {
      try {
        await transactionsAPI.delete(id);
        loadData();
      } catch (error) {
        console.error('刪除失敗:', error);
      }
    }
  };

  const filteredCategories = categories.filter(c => c.type === form.type);

  // 自訂 Tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const total = payload.reduce((sum, entry) => sum + entry.value, 0);
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '12px',
          border: '1px solid #ddd',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>{label}</p>
          {payload.map((entry, index) => (
            entry.value > 0 && (
              <p key={index} style={{ 
                color: entry.color, 
                margin: '4px 0',
                fontSize: '0.9rem'
              }}>
                {entry.name}: ${entry.value.toLocaleString()}
              </p>
            )
          ))}
          <p style={{ 
            borderTop: '1px solid #eee', 
            paddingTop: '8px', 
            marginTop: '8px',
            fontWeight: 'bold'
          }}>
            合計: ${total.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>📝 交易記錄</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新增交易
        </button>
      </div>

      {/* 時間範圍選擇 & 統計卡片 */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h3 style={{ margin: 0 }}>📊 {getTimeRangeLabel()}收支統計</h3>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid #ddd',
              fontSize: '0.95rem',
              cursor: 'pointer'
            }}
          >
            <option value="week">本週</option>
            <option value="month">本月</option>
            <option value="year">今年</option>
          </select>
        </div>

        {/* 統計數字 */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '15px',
          marginBottom: '20px'
        }}>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e8f5e9', 
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ color: '#666', fontSize: '0.9rem' }}>收入</div>
            <div style={{ color: '#27ae60', fontSize: '1.5rem', fontWeight: 'bold' }}>
              +${stats.income.toLocaleString()}
            </div>
          </div>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#ffebee', 
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ color: '#666', fontSize: '0.9rem' }}>支出</div>
            <div style={{ color: '#e74c3c', fontSize: '1.5rem', fontWeight: 'bold' }}>
              -${stats.expense.toLocaleString()}
            </div>
          </div>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e3f2fd', 
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ color: '#666', fontSize: '0.9rem' }}>結餘</div>
            <div style={{ 
              color: stats.net >= 0 ? '#27ae60' : '#e74c3c', 
              fontSize: '1.5rem', 
              fontWeight: 'bold' 
            }}>
              {stats.net >= 0 ? '+' : ''}${stats.net.toLocaleString()}
            </div>
          </div>
        </div>

        {/* 每日支出堆疊長條圖 */}
        {chartData.data.length > 0 && (
          <div>
            <h4 style={{ marginBottom: '15px', color: '#666' }}>📈 每日支出分佈</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData.data}>
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                {chartData.categories.map((cat, index) => (
                  <Bar
                    key={cat}
                    dataKey={cat}
                    stackId="expense"
                    fill={getCategoryColor(cat, index)}
                    name={cat}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {chartData.data.length === 0 && (
          <p style={{ textAlign: 'center', color: '#999', padding: '30px' }}>
            {getTimeRangeLabel()}尚無支出記錄
          </p>
        )}
      </div>

      {/* 交易列表 */}
      <div className="card">
        <h3 style={{ marginBottom: '15px' }}>📋 {getTimeRangeLabel()}交易明細</h3>
        <table className="table">
          <thead>
            <tr>
              <th>日期</th>
              <th>說明</th>
              <th>分類</th>
              <th>金額</th>
              <th>類型</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map(t => (
              <tr key={t.id}>
                <td>{t.date}</td>
                <td>{t.description}</td>
                <td>
                  {categories.find(c => c.id === t.category_id)?.icon}{' '}
                  {categories.find(c => c.id === t.category_id)?.name || '-'}
                </td>
                <td style={{ color: t.type === 'income' ? '#27ae60' : '#e74c3c' }}>
                  {t.type === 'income' ? '+' : '-'}${t.amount?.toLocaleString()}
                </td>
                <td>
                  <span className={`tag tag-${t.type}`}>
                    {t.type === 'income' ? '收入' : '支出'}
                  </span>
                </td>
                <td>
                  <button 
                    className="btn btn-danger btn-small"
                    onClick={() => handleDelete(t.id)}
                  >
                    刪除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredTransactions.length === 0 && (
          <p style={{ textAlign: 'center', color: '#999', padding: '30px' }}>
            {getTimeRangeLabel()}尚無交易記錄
          </p>
        )}
      </div>

      {/* 新增交易 Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>新增交易</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>類型</label>
                <select
                  value={form.type}
                  onChange={e => setForm({ ...form, type: e.target.value, category_id: '' })}
                >
                  <option value="expense">支出</option>
                  <option value="income">收入</option>
                </select>
              </div>
              <div className="form-group">
                <label>說明</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="例如：星巴克咖啡"
                  required
                />
              </div>
              <div className="form-group">
                <label>金額</label>
                <input
                  type="number"
                  value={form.amount}
                  onChange={e => setForm({ ...form, amount: e.target.value })}
                  placeholder="0"
                  required
                />
              </div>
              <div className="form-group">
                <label>分類（可留空，系統會自動分類）</label>
                <select
                  value={form.category_id}
                  onChange={e => setForm({ ...form, category_id: e.target.value })}
                >
                  <option value="">自動分類</option>
                  {filteredCategories.map(c => (
                    <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>日期</label>
                <input
                  type="date"
                  value={form.date}
                  onChange={e => setForm({ ...form, date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>帳戶</label>
                <select
                  value={form.account_id}
                  onChange={e => setForm({ ...form, account_id: e.target.value })}
                >
                  <option value="">選擇帳戶</option>
                  {accounts.map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowModal(false)}>
                  取消
                </button>
                <button type="submit" className="btn btn-primary">
                  儲存
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Transactions;