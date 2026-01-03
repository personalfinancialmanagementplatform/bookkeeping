import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import './Portfolio.css';

const API_BASE = 'http://localhost:5005/api';

const ASSET_TYPES = {
  stock: { label: '股票', color: '#e74c3c' },
  etf: { label: 'ETF', color: '#3498db' },
  bond: { label: '債券', color: '#2ecc71' },
  fund: { label: '基金', color: '#f39c12' },
  other: { label: '其他', color: '#95a5a6' }
};

function Portfolio() {
  const [activeTab, setActiveTab] = useState('holdings');
  const [summary, setSummary] = useState(null);
  const [monthlyStats, setMonthlyStats] = useState(null);
  const [holdings, setHoldings] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filterType, setFilterType] = useState('all');
  
  const [newHolding, setNewHolding] = useState({
    account_id: 1,
    symbol: '',
    name: '',
    quantity: '',
    price: '',
    asset_type: 'stock',
    transaction_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryRes, watchlistRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/portfolio/summary`),
        fetch(`${API_BASE}/watchlist`),
        fetch(`${API_BASE}/portfolio/monthly-stats`)
      ]);
      
      const summaryData = await summaryRes.json();
      const watchlistData = await watchlistRes.json();
      const statsData = await statsRes.json();
      
      setSummary(summaryData);
      setHoldings(summaryData.holdings || []);
      setWatchlist(watchlistData);
      setMonthlyStats(statsData);
    } catch (error) {
      console.error('載入失敗:', error);
    }
    setLoading(false);
  };

  const searchStocks = async (keyword) => {
    if (keyword.length < 1) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/stocks/search?q=${keyword}`);
      const data = await res.json();
      setSearchResults(data.slice(0, 10));
    } catch (error) {
      console.error('搜尋失敗:', error);
    }
  };

  const selectStock = async (stock) => {
    const assetType = stock.type === 'ETF' ? 'etf' : 'stock';
    setNewHolding({
      ...newHolding,
      symbol: stock.symbol,
      name: stock.name,
      asset_type: assetType
    });
    setSearchResults([]);
    setSearchKeyword(stock.symbol + ' ' + stock.name);
    
    try {
      const res = await fetch(`${API_BASE}/stocks/quote/${stock.symbol}`);
      const quote = await res.json();
      if (quote.success) {
        setNewHolding(prev => ({ ...prev, price: quote.price }));
      }
    } catch (error) {
      console.error('取得股價失敗:', error);
    }
  };

  const handleAddHolding = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/holdings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newHolding)
      });
      
      if (res.ok) {
        setShowAddModal(false);
        setNewHolding({ 
          account_id: 1, symbol: '', name: '', quantity: '', price: '', 
          asset_type: 'stock', transaction_date: new Date().toISOString().split('T')[0] 
        });
        setSearchKeyword('');
        loadData();
      }
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  const handleAddToWatchlist = async (stock) => {
    try {
      const res = await fetch(`${API_BASE}/watchlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: stock.symbol, name: stock.name })
      });
      
      if (res.ok) {
        setShowWatchlistModal(false);
        setSearchKeyword('');
        setSearchResults([]);
        loadData();
      }
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  const handleRemoveFromWatchlist = async (id) => {
    if (!window.confirm('確定要移除嗎？')) return;
    try {
      await fetch(`${API_BASE}/watchlist/${id}`, { method: 'DELETE' });
      loadData();
    } catch (error) {
      console.error('移除失敗:', error);
    }
  };

  const filteredHoldings = filterType === 'all' 
    ? holdings 
    : holdings.filter(h => h.asset_type === filterType);

  const groupedHoldings = filteredHoldings.reduce((groups, h) => {
    const type = h.asset_type || 'other';
    if (!groups[type]) groups[type] = [];
    groups[type].push(h);
    return groups;
  }, {});

  const pieData = Object.entries(summary?.allocation || {}).map(([type, data]) => ({
    name: ASSET_TYPES[type]?.label || type,
    value: data.value,
    percentage: data.percentage,
    color: ASSET_TYPES[type]?.color || '#95a5a6'
  })).filter(d => d.value > 0);

  const getTransactionTypeLabel = (type) => {
    const labels = { buy: '買入', sell: '賣出', dividend: '股息' };
    return labels[type] || type;
  };

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  return (
    <div className="portfolio-page">
      <div className="page-header">
        <h1>📈 投資組合</h1>
        <button className="btn-primary" onClick={() => setShowAddModal(true)}>
          + 新增持倉
        </button>
      </div>

      {/* 頂部統計卡片 - 橫向排列 */}
      <div className="stats-row">
        <div className="stat-card-h">
          <span className="stat-icon">💰</span>
          <div className="stat-content">
            <span className="stat-label">總市值</span>
            <span className="stat-value">NT$ {summary?.total_value?.toLocaleString()}</span>
          </div>
        </div>
        <div className="stat-card-h">
          <span className="stat-icon">💵</span>
          <div className="stat-content">
            <span className="stat-label">總成本</span>
            <span className="stat-value">NT$ {summary?.total_cost?.toLocaleString()}</span>
          </div>
        </div>
        <div className={`stat-card-h ${summary?.total_profit >= 0 ? 'profit' : 'loss'}`}>
          <span className="stat-icon">{summary?.total_profit >= 0 ? '📈' : '📉'}</span>
          <div className="stat-content">
            <span className="stat-label">未實現損益</span>
            <span className="stat-value">
              {summary?.total_profit >= 0 ? '+' : ''}NT$ {summary?.total_profit?.toLocaleString()}
              <small> ({summary?.total_profit_rate}%)</small>
            </span>
          </div>
        </div>
        <div className="stat-card-h">
          <span className="stat-icon">📊</span>
          <div className="stat-content">
            <span className="stat-label">持倉數量</span>
            <span className="stat-value">{summary?.holdings_count} 檔</span>
          </div>
        </div>
      </div>

      {/* 本月統計 + 資產配置 + 最近交易 */}
      <div className="middle-section">
        {/* 本月投資統計 */}
        <div className="card monthly-card">
          <h3>📅 本月投資</h3>
          <div className="monthly-grid">
            <div className="monthly-item expense">
              <span className="label">投資支出</span>
              <span className="value">-${monthlyStats?.monthly_investment?.toLocaleString() || 0}</span>
            </div>
            <div className="monthly-item income">
              <span className="label">賣出收入</span>
              <span className="value">+${monthlyStats?.monthly_sell?.toLocaleString() || 0}</span>
            </div>
            <div className="monthly-item dividend">
              <span className="label">股息收入</span>
              <span className="value">+${monthlyStats?.monthly_dividend?.toLocaleString() || 0}</span>
            </div>
            <div className={`monthly-item ${monthlyStats?.monthly_profit >= 0 ? 'profit' : 'loss'}`}>
              <span className="label">本月損益</span>
              <span className="value">
                {monthlyStats?.monthly_profit >= 0 ? '+' : ''}${monthlyStats?.monthly_profit?.toLocaleString() || 0}
              </span>
            </div>
          </div>
        </div>

        {/* 資產配置圓餅圖 */}
        <div className="card chart-card">
          <h3>📊 資產配置</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `NT$ ${value.toLocaleString()}`} />
                <Legend formatter={(value, entry) => {
                  const item = pieData.find(d => d.name === value);
                  return `${value} (${item?.percentage || 0}%)`;
                }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-chart">尚無資產配置</div>
          )}
        </div>

        {/* 最近交易 */}
        <div className="card recent-card">
          <h3>🕐 最近交易</h3>
          {monthlyStats?.recent_transactions?.length > 0 ? (
            <ul className="recent-list">
              {monthlyStats.recent_transactions.map((t, i) => (
                <li key={i} className={`recent-item ${t.type}`}>
                  <div className="item-left">
                    <span className={`type-badge ${t.type}`}>{getTransactionTypeLabel(t.type)}</span>
                    <span className="stock-name">{t.symbol}</span>
                  </div>
                  <div className="item-right">
                    <span className="amount">
                      {t.type === 'buy' ? '-' : '+'}${t.amount?.toLocaleString()}
                    </span>
                    <span className="date">{t.date}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="empty-chart">尚無交易記錄</div>
          )}
        </div>
      </div>

      {/* 頁籤 */}
      <div className="tabs">
        <button className={activeTab === 'holdings' ? 'active' : ''} onClick={() => setActiveTab('holdings')}>
          持倉明細
        </button>
        <button className={activeTab === 'watchlist' ? 'active' : ''} onClick={() => setActiveTab('watchlist')}>
          關注清單
        </button>
      </div>

      {/* 持倉列表 */}
      {activeTab === 'holdings' && (
        <div className="holdings-section">
          <div className="filter-bar">
            <span>篩選：</span>
            <button className={filterType === 'all' ? 'active' : ''} onClick={() => setFilterType('all')}>全部</button>
            {Object.entries(ASSET_TYPES).map(([type, info]) => (
              <button key={type} className={filterType === type ? 'active' : ''} onClick={() => setFilterType(type)}>
                {info.label}
              </button>
            ))}
          </div>

          {holdings.length === 0 ? (
            <div className="empty-state">
              <p>尚未新增任何持倉</p>
              <button className="btn-primary" onClick={() => setShowAddModal(true)}>新增第一筆持倉</button>
            </div>
          ) : (
            <div className="holdings-by-type">
              {Object.entries(groupedHoldings).map(([type, typeHoldings]) => (
                <div key={type} className="type-group">
                  <h3 className="type-header">
                    <span className="type-dot" style={{ background: ASSET_TYPES[type]?.color }}></span>
                    {ASSET_TYPES[type]?.label || type}
                    <span className="type-count">({typeHoldings.length} 檔)</span>
                  </h3>
                  <table className="holdings-table">
                    <thead>
                      <tr>
                        <th>標的</th>
                        <th>數量</th>
                        <th>成本價</th>
                        <th>現價</th>
                        <th>市值</th>
                        <th>損益</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      {typeHoldings.map(h => (
                        <tr key={h.id}>
                          <td><strong>{h.symbol}</strong><br /><small>{h.name}</small></td>
                          <td>{h.quantity}</td>
                          <td>NT$ {h.average_cost?.toFixed(2)}</td>
                          <td>NT$ {h.current_price?.toFixed(2)}</td>
                          <td>NT$ {h.market_value?.toLocaleString()}</td>
                          <td className={h.profit >= 0 ? 'profit' : 'loss'}>
                            {h.profit >= 0 ? '+' : ''}NT$ {h.profit?.toLocaleString()}
                            <br /><small>({h.profit_rate}%)</small>
                          </td>
                          <td>
                            <button className="btn-sell" onClick={() => alert('賣出功能開發中')}>賣出</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 關注清單 */}
      {activeTab === 'watchlist' && (
        <div className="watchlist-section">
          <div className="section-header">
            <button className="btn-secondary" onClick={() => setShowWatchlistModal(true)}>+ 新增關注</button>
          </div>
          {watchlist.length === 0 ? (
            <div className="empty-state"><p>尚未新增任何關注標的</p></div>
          ) : (
            <div className="watchlist-grid">
              {watchlist.map(w => (
                <div key={w.id} className="watchlist-card">
                  <div className="card-header">
                    <div><strong>{w.symbol}</strong><span className="name">{w.name}</span></div>
                    <button className="btn-remove" onClick={() => handleRemoveFromWatchlist(w.id)}>✕</button>
                  </div>
                  <div className="card-body">
                    <span className="price">NT$ {w.current_price?.toFixed(2) || '-'}</span>
                    <span className={`change ${(w.change || 0) >= 0 ? 'up' : 'down'}`}>
                      {(w.change || 0) >= 0 ? '▲' : '▼'} {Math.abs(w.change || 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 新增持倉 Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>新增持倉</h3>
            <form onSubmit={handleAddHolding}>
              <div className="form-group">
                <label>搜尋股票</label>
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => { setSearchKeyword(e.target.value); searchStocks(e.target.value); }}
                  placeholder="輸入代號或名稱..."
                />
                {searchResults.length > 0 && (
                  <ul className="search-results">
                    {searchResults.map(s => (
                      <li key={s.symbol} onClick={() => selectStock(s)}>
                        <strong>{s.symbol}</strong> {s.name}<span className="badge">{s.type}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="form-group">
                <label>資產類型</label>
                <select value={newHolding.asset_type} onChange={(e) => setNewHolding({...newHolding, asset_type: e.target.value})}>
                  {Object.entries(ASSET_TYPES).map(([type, info]) => (
                    <option key={type} value={type}>{info.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>購買日期</label>
                <input 
                  type="date" 
                  value={newHolding.transaction_date} 
                  onChange={(e) => setNewHolding({...newHolding, transaction_date: e.target.value})}
                  required 
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>數量（股）</label>
                  <input type="number" value={newHolding.quantity} onChange={(e) => setNewHolding({...newHolding, quantity: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>買入價格</label>
                  <input type="number" step="0.01" value={newHolding.price} onChange={(e) => setNewHolding({...newHolding, price: e.target.value})} required />
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={() => setShowAddModal(false)}>取消</button>
                <button type="submit" className="btn-primary">確認新增</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 新增關注 Modal */}
      {showWatchlistModal && (
        <div className="modal-overlay" onClick={() => setShowWatchlistModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>新增關注標的</h3>
            <div className="form-group">
              <label>搜尋股票</label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => { setSearchKeyword(e.target.value); searchStocks(e.target.value); }}
                placeholder="輸入代號或名稱..."
              />
              {searchResults.length > 0 && (
                <ul className="search-results">
                  {searchResults.map(s => (
                    <li key={s.symbol} onClick={() => handleAddToWatchlist(s)}>
                      <strong>{s.symbol}</strong> {s.name}<span className="badge">{s.type}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="form-actions">
              <button className="btn-cancel" onClick={() => setShowWatchlistModal(false)}>關閉</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Portfolio;