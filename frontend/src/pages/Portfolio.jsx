import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import './Portfolio.css';

const API_BASE = 'http://localhost:5005/api';

// 資產類型設定
const ASSET_TYPES = {
  stock: { label: '股票', color: '#e74c3c' },
  etf: { label: 'ETF', color: '#3498db' },
  bond: { label: '債券', color: '#2ecc71' },
  fund: { label: '基金', color: '#f39c12' }
};

function Portfolio() {
  const [activeTab, setActiveTab] = useState('holdings');
  const [summary, setSummary] = useState(null);
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
    asset_type: 'stock'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryRes, watchlistRes] = await Promise.all([
        fetch(`${API_BASE}/portfolio/summary`),
        fetch(`${API_BASE}/watchlist`)
      ]);
      
      const summaryData = await summaryRes.json();
      const watchlistData = await watchlistRes.json();
      
      setSummary(summaryData);
      setHoldings(summaryData.holdings || []);
      setWatchlist(watchlistData);
    } catch (error) {
      console.error('載入失敗:', error);
    }
    setLoading(false);
  };

  // 搜尋股票
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

  // 選擇股票
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

  // 新增持倉
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
        setNewHolding({ account_id: 1, symbol: '', name: '', quantity: '', price: '', asset_type: 'stock' });
        setSearchKeyword('');
        loadData();
      }
    } catch (error) {
      console.error('新增失敗:', error);
    }
  };

  // 新增到關注清單
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

  // 從關注清單移除
  const handleRemoveFromWatchlist = async (id) => {
    if (!window.confirm('確定要移除嗎？')) return;
    try {
      await fetch(`${API_BASE}/watchlist/${id}`, { method: 'DELETE' });
      loadData();
    } catch (error) {
      console.error('移除失敗:', error);
    }
  };

  // 篩選持倉
  const filteredHoldings = filterType === 'all' 
    ? holdings 
    : holdings.filter(h => h.asset_type === filterType);

  // 按類別分組
  const groupedHoldings = filteredHoldings.reduce((groups, h) => {
    const type = h.asset_type || 'stock';
    if (!groups[type]) groups[type] = [];
    groups[type].push(h);
    return groups;
  }, {});

  // 圓餅圖資料
  const pieData = Object.entries(summary?.allocation || {}).map(([type, data]) => ({
    name: ASSET_TYPES[type]?.label || type,
    value: data.value,
    percentage: data.percentage,
    color: ASSET_TYPES[type]?.color || '#95a5a6'
  })).filter(d => d.value > 0);

  if (loading) {
    return <div className="loading">載入中...</div>;
  }

  return (
    <div className="portfolio-page">
      <div className="page-header">
        <h1>📈 投資組合</h1>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => setShowAddModal(true)}>
            + 新增持倉
          </button>
        </div>
      </div>

      {/* 摘要卡片 */}
      {summary && (
        <div className="summary-section">
          <div className="summary-cards">
            <div className="summary-card">
              <span className="label">總市值</span>
              <span className="value">NT$ {summary.total_value?.toLocaleString()}</span>
            </div>
            <div className="summary-card">
              <span className="label">總成本</span>
              <span className="value">NT$ {summary.total_cost?.toLocaleString()}</span>
            </div>
            <div className={`summary-card ${summary.total_profit >= 0 ? 'profit' : 'loss'}`}>
              <span className="label">未實現損益</span>
              <span className="value">
                {summary.total_profit >= 0 ? '+' : ''}NT$ {summary.total_profit?.toLocaleString()}
                <small> ({summary.total_profit_rate}%)</small>
              </span>
            </div>
            <div className="summary-card">
              <span className="label">持倉數量</span>
              <span className="value">{summary.holdings_count} 檔</span>
            </div>
          </div>

          {/* 圓餅圖 */}
          {pieData.length > 0 && (
            <div className="chart-section">
              <h3>資產配置</h3>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => `NT$ ${value.toLocaleString()}`}
                    />
                    <Legend 
                      formatter={(value, entry) => {
                        const item = pieData.find(d => d.name === value);
                        return `${value} (${item?.percentage || 0}%)`;
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 頁籤 */}
      <div className="tabs">
        <button 
          className={activeTab === 'holdings' ? 'active' : ''} 
          onClick={() => setActiveTab('holdings')}
        >
          持倉明細
        </button>
        <button 
          className={activeTab === 'watchlist' ? 'active' : ''} 
          onClick={() => setActiveTab('watchlist')}
        >
          關注清單
        </button>
      </div>

      {/* 持倉列表 */}
      {activeTab === 'holdings' && (
        <div className="holdings-section">
          {/* 篩選器 */}
          <div className="filter-bar">
            <span>篩選：</span>
            <button 
              className={filterType === 'all' ? 'active' : ''} 
              onClick={() => setFilterType('all')}
            >
              全部
            </button>
            {Object.entries(ASSET_TYPES).map(([type, info]) => (
              <button 
                key={type}
                className={filterType === type ? 'active' : ''} 
                onClick={() => setFilterType(type)}
              >
                {info.label}
              </button>
            ))}
          </div>

          {holdings.length === 0 ? (
            <div className="empty-state">
              <p>尚未新增任何持倉</p>
              <button className="btn-primary" onClick={() => setShowAddModal(true)}>
                新增第一筆持倉
              </button>
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
                      </tr>
                    </thead>
                    <tbody>
                      {typeHoldings.map(h => (
                        <tr key={h.id}>
                          <td>
                            <strong>{h.symbol}</strong>
                            <br /><small>{h.name}</small>
                          </td>
                          <td>{h.quantity}</td>
                          <td>NT$ {h.average_cost?.toFixed(2)}</td>
                          <td>NT$ {h.current_price?.toFixed(2)}</td>
                          <td>NT$ {h.market_value?.toLocaleString()}</td>
                          <td className={h.profit >= 0 ? 'profit' : 'loss'}>
                            {h.profit >= 0 ? '+' : ''}NT$ {h.profit?.toLocaleString()}
                            <br /><small>({h.profit_rate}%)</small>
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
            <button className="btn-secondary" onClick={() => setShowWatchlistModal(true)}>
              + 新增關注
            </button>
          </div>
          
          {watchlist.length === 0 ? (
            <div className="empty-state">
              <p>尚未新增任何關注標的</p>
            </div>
          ) : (
            <div className="watchlist-grid">
              {watchlist.map(w => (
                <div key={w.id} className="watchlist-card">
                  <div className="card-header">
                    <div>
                      <strong>{w.symbol}</strong>
                      <span className="name">{w.name}</span>
                    </div>
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
                  onChange={(e) => {
                    setSearchKeyword(e.target.value);
                    searchStocks(e.target.value);
                  }}
                  placeholder="輸入代號或名稱..."
                />
                {searchResults.length > 0 && (
                  <ul className="search-results">
                    {searchResults.map(s => (
                      <li key={s.symbol} onClick={() => selectStock(s)}>
                        <strong>{s.symbol}</strong> {s.name}
                        <span className="badge">{s.type}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="form-group">
                <label>資產類型</label>
                <select
                  value={newHolding.asset_type}
                  onChange={(e) => setNewHolding({...newHolding, asset_type: e.target.value})}
                >
                  {Object.entries(ASSET_TYPES).map(([type, info]) => (
                    <option key={type} value={type}>{info.label}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>數量（股）</label>
                  <input
                    type="number"
                    value={newHolding.quantity}
                    onChange={(e) => setNewHolding({...newHolding, quantity: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>買入價格</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newHolding.price}
                    onChange={(e) => setNewHolding({...newHolding, price: e.target.value})}
                    required
                  />
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
                onChange={(e) => {
                  setSearchKeyword(e.target.value);
                  searchStocks(e.target.value);
                }}
                placeholder="輸入代號或名稱..."
              />
              {searchResults.length > 0 && (
                <ul className="search-results">
                  {searchResults.map(s => (
                    <li key={s.symbol} onClick={() => handleAddToWatchlist(s)}>
                      <strong>{s.symbol}</strong> {s.name}
                      <span className="badge">{s.type}</span>
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