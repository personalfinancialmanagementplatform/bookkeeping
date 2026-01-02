import { useState, useEffect } from 'react';
import { transactionsAPI, categoriesAPI, accountsAPI } from '../services/api';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [showModal, setShowModal] = useState(false);
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>📝 交易記錄</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新增交易
        </button>
      </div>

      <div className="card">
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
            {transactions.map(t => (
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
        {transactions.length === 0 && (
          <p style={{ textAlign: 'center', color: '#999', padding: '30px' }}>
            尚無交易記錄
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