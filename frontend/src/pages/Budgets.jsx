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
    period: 'monthly',
    start_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [budgetsRes, catRes] = await Promise.all([
        budgetsAPI.getAll(),
        categoriesAPI.getAll('expense')
      ]);
      setBudgets(budgetsRes.data);
      setCategories(catRes.data);
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
        category_id: parseInt(form.category_id)
      });
      setShowModal(false);
      setForm({
        name: '',
        amount: '',
        category_id: '',
        period: 'monthly',
        start_date: new Date().toISOString().split('T')[0]
      });
      loadData();
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  const getProgressClass = (percent) => {
    if (percent >= 100) return 'danger';
    if (percent >= 80) return 'warning';
    return '';
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
                  <option value="daily">每日</option>
                  <option value="weekly">每週</option>
                  <option value="monthly">每月</option>
                  <option value="yearly">每年</option>
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