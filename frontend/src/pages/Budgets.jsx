import { useState, useEffect } from 'react';
import { budgetsAPI, categoriesAPI } from '../services/api';

function Budgets() {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    name: '',
    amount: '',
    category_id: '',
    period: 'this_month',
    start_date: new Date().toISOString().split('T')[0],
    end_date: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      let budgetsData = [];
      let categoriesData = [];
      
      try {
        const budgetsRes = await budgetsAPI.getAll();
        budgetsData = budgetsRes.data || [];
      } catch (e) {
        console.error('載入預算失敗:', e);
      }
      
      try {
        const catRes = await categoriesAPI.getAll();
        categoriesData = catRes.data || [];
      } catch (e) {
        console.error('載入分類失敗:', e);
      }
      
      setBudgets(budgetsData);
      const expenseCategories = categoriesData.filter(c => c.type === 'expense');
      setCategories(expenseCategories);
      
    } catch (error) {
      console.error('載入失敗:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await budgetsAPI.create({
        ...form,
        amount: parseFloat(form.amount),
        category_id: parseInt(form.category_id),
        end_date: form.end_date || null
      });
      setShowModal(false);
      setForm({
        name: '',
        amount: '',
        category_id: '',
        period: 'this_month',
        start_date: new Date().toISOString().split('T')[0],
        end_date: ''
      });
      loadData();
    } catch (error) {
      console.error('新增失敗:', error);
      alert('新增失敗，請檢查所有欄位是否填寫正確');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('確定要刪除這個預算嗎？')) {
      try {
        await budgetsAPI.delete(id);
        loadData();
      } catch (error) {
        console.error('刪除失敗:', error);
      }
    }
  };

  const getProgressClass = (percent) => {
    if (percent >= 100) return 'danger';
    if (percent >= 80) return 'warning';
    return '';
  };

  const getPeriodLabel = (period) => {
    const labels = {
      'today': '本日',
      'this_week': '本週',
      'this_month': '本月',
      'this_year': '本年',
      'daily': '每日',
      'weekly': '每週',
      'monthly': '每月',
      'yearly': '每年'
    };
    return labels[period] || period;
  };

  const getDaysRemainingLabel = (days) => {
    if (days === null || days === undefined) return null;
    if (days < 0) return <span style={{ color: '#e74c3c' }}>已過期</span>;
    if (days === 0) return <span style={{ color: '#e74c3c' }}>今日到期</span>;
    if (days <= 3) return <span style={{ color: '#f39c12' }}>剩餘 {days} 天</span>;
    if (days <= 7) return <span style={{ color: '#3498db' }}>剩餘 {days} 天</span>;
    return <span style={{ color: '#666' }}>剩餘 {days} 天</span>;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>📈 預算管理</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新增預算
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {budgets.map(budget => (
          <div key={budget.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0 }}>
                {budget.category_icon} {budget.name}
              </h3>
              <span className={`tag ${budget.status === 'over' ? 'tag-expense' : 'tag-income'}`}>
                {budget.status === 'over' ? '超支' : budget.status === 'warning' ? '警告' : '正常'}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', color: '#666', fontSize: '0.85rem' }}>
              <span>週期：{getPeriodLabel(budget.period)}</span>
              {getDaysRemainingLabel(budget.days_remaining)}
            </div>
            
            <div style={{ marginBottom: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span>已使用: ${budget.spent?.toLocaleString()}</span>
                <span>預算: ${budget.amount?.toLocaleString()}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress ${getProgressClass(budget.usage_percent)}`}
                  style={{ width: `${Math.min(budget.usage_percent, 100)}%` }}
                />
              </div>
              <div style={{ textAlign: 'right', marginTop: '5px', color: '#666', fontSize: '0.9rem' }}>
                {budget.usage_percent?.toFixed(1)}%
              </div>
            </div>

            <div style={{ color: budget.remaining >= 0 ? '#27ae60' : '#e74c3c', fontWeight: 'bold' }}>
              剩餘: ${budget.remaining?.toLocaleString()}
            </div>

            <button 
              className="btn btn-danger btn-small"
              style={{ marginTop: '15px', width: '100%' }}
              onClick={() => handleDelete(budget.id)}
            >
              刪除預算
            </button>
          </div>
        ))}
      </div>

      {budgets.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: '#999' }}>
          尚無預算設定，點擊「新增預算」開始管理您的支出
        </div>
      )}

      {/* 新增預算 Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>新增預算</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>預算名稱</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  placeholder="例如：每月餐飲"
                  required
                />
              </div>
              <div className="form-group">
                <label>分類</label>
                <select
                  value={form.category_id}
                  onChange={e => setForm({ ...form, category_id: e.target.value })}
                  required
                >
                  <option value="">選擇分類</option>
                  {categories.map(c => (
                    <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>預算金額</label>
                <input
                  type="number"
                  value={form.amount}
                  onChange={e => setForm({ ...form, amount: e.target.value })}
                  placeholder="0"
                  required
                />
              </div>
              <div className="form-group">
                <label>週期</label>
                <select
                  value={form.period}
                  onChange={e => setForm({ ...form, period: e.target.value })}
                >
                  <optgroup label="📅 本期預算">
                    <option value="today">本日</option>
                    <option value="this_week">本週</option>
                    <option value="this_month">本月</option>
                    <option value="this_year">本年</option>
                  </optgroup>
                  <optgroup label="🔄 週期預算">
                    <option value="daily">每日</option>
                    <option value="weekly">每週</option>
                    <option value="monthly">每月</option>
                    <option value="yearly">每年</option>
                  </optgroup>
                </select>
              </div>
              <div className="form-group">
                <label>開始日期</label>
                <input
                  type="date"
                  value={form.start_date}
                  onChange={e => setForm({ ...form, start_date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>結束日期（可選，用於計算剩餘天數）</label>
                <input
                  type="date"
                  value={form.end_date}
                  onChange={e => setForm({ ...form, end_date: e.target.value })}
                />
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

export default Budgets;