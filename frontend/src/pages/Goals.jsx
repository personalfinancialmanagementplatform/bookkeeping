import { useState, useEffect } from 'react';
import { goalsAPI } from '../services/api';

function Goals() {
  const [goals, setGoals] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showAddMoneyModal, setShowAddMoneyModal] = useState(null);
  const [addAmount, setAddAmount] = useState('');
  const [form, setForm] = useState({
    name: '',
    target_amount: '',
    current_amount: '0',
    deadline: '',
    priority: '3',
    description: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await goalsAPI.getAll();
      setGoals(res.data);
    } catch (error) {
      console.error('載入失敗:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await goalsAPI.create({
        ...form,
        target_amount: parseFloat(form.target_amount),
        current_amount: parseFloat(form.current_amount),
        priority: parseInt(form.priority)
      });
      setShowModal(false);
      setForm({
        name: '',
        target_amount: '',
        current_amount: '0',
        deadline: '',
        priority: '3',
        description: ''
      });
      loadData();
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  const handleAddMoney = async (goalId) => {
    try {
      await goalsAPI.addMoney(goalId, parseFloat(addAmount));
      setShowAddMoneyModal(null);
      setAddAmount('');
      loadData();
    } catch (error) {
      console.error('新增存款失敗:', error);
    }
  };

  const getPriorityStars = (priority) => {
    return '⭐'.repeat(priority);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>🎯 財務目標</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新增目標
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
        {goals.map(goal => (
          <div key={goal.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0 }}>🎯 {goal.name}</h3>
              <span className={`tag ${goal.status === 'completed' ? 'tag-income' : 'tag-expense'}`}>
                {goal.status === 'completed' ? '已達成' : '進行中'}
              </span>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span>目前: ${goal.current_amount?.toLocaleString()}</span>
                <span>目標: ${goal.target_amount?.toLocaleString()}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress"
                  style={{ 
                    width: `${Math.min(goal.progress, 100)}%`,
                    background: goal.status === 'completed' ? '#27ae60' : '#3498db'
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px', color: '#666', fontSize: '0.9rem' }}>
                <span>{goal.progress?.toFixed(1)}%</span>
                <span>還差 ${goal.remaining_amount?.toLocaleString()}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span>優先級: {getPriorityStars(goal.priority)}</span>
              {goal.deadline && (
                <span style={{ color: goal.days_remaining < 30 ? '#e74c3c' : '#666' }}>
                  📅 {goal.deadline} ({goal.days_remaining}天)
                </span>
              )}
            </div>

            {goal.description && (
              <p style={{ color: '#666', fontSize: '0.9rem', marginBottom: '15px' }}>
                {goal.description}
              </p>
            )}

            {goal.status !== 'completed' && (
              <button 
                className="btn btn-success"
                style={{ width: '100%' }}
                onClick={() => setShowAddMoneyModal(goal.id)}
              >
                💰 存入金額
              </button>
            )}
          </div>
        ))}
      </div>

      {goals.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: '#999' }}>
          尚無財務目標，點擊「新增目標」開始規劃您的儲蓄計畫
        </div>
      )}

      {/* 新增目標 Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>新增財務目標</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>目標名稱</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  placeholder="例如：日本旅遊基金"
                  required
                />
              </div>
              <div className="form-group">
                <label>目標金額</label>
                <input
                  type="number"
                  value={form.target_amount}
                  onChange={e => setForm({ ...form, target_amount: e.target.value })}
                  placeholder="50000"
                  required
                />
              </div>
              <div className="form-group">
                <label>目前已有金額</label>
                <input
                  type="number"
                  value={form.current_amount}
                  onChange={e => setForm({ ...form, current_amount: e.target.value })}
                  placeholder="0"
                />
              </div>
              <div className="form-group">
                <label>目標日期</label>
                <input
                  type="date"
                  value={form.deadline}
                  onChange={e => setForm({ ...form, deadline: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>優先級 (1-5)</label>
                <select
                  value={form.priority}
                  onChange={e => setForm({ ...form, priority: e.target.value })}
                >
                  <option value="1">1 ⭐</option>
                  <option value="2">2 ⭐⭐</option>
                  <option value="3">3 ⭐⭐⭐</option>
                  <option value="4">4 ⭐⭐⭐⭐</option>
                  <option value="5">5 ⭐⭐⭐⭐⭐</option>
                </select>
              </div>
              <div className="form-group">
                <label>說明</label>
                <textarea
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="目標說明..."
                  rows="3"
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

      {/* 存入金額 Modal */}
      {showAddMoneyModal && (
        <div className="modal-overlay" onClick={() => setShowAddMoneyModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>💰 存入金額</h3>
            <div className="form-group">
              <label>金額</label>
              <input
                type="number"
                value={addAmount}
                onChange={e => setAddAmount(e.target.value)}
                placeholder="輸入要存入的金額"
              />
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowAddMoneyModal(null)}>
                取消
              </button>
              <button 
                className="btn btn-success"
                onClick={() => handleAddMoney(showAddMoneyModal)}
              >
                確認存入
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Goals;