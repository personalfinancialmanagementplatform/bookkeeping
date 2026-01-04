import { useEffect, useMemo, useState } from 'react';

function Learn() {
  const [items, setItems] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const [query, setQuery] = useState('');
  const [level, setLevel] = useState('all');

  const [form, setForm] = useState({
    title: '',
    topic: '',
    level: 'beginner', // beginner | intermediate | advanced
    content: '',
    example: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    // 先用前端內建資料（之後你要接後端 API，再把這裡改成 axios 呼叫）
    const seed = [
      {
        id: 1,
        title: '複利是什麼？為什麼越早開始越有利？',
        topic: '複利',
        level: 'beginner',
        content: '複利=利滾利。利息會再產生利息。時間越久，效果越明顯。',
        example: '例：10,000 元，年利率 6%。1 年後 10,600；2 年後 11,236（=10,600×1.06）。'
      },
      {
        id: 2,
        title: 'ETF 跟股票差在哪？',
        topic: 'ETF',
        level: 'beginner',
        content: 'ETF 多數追蹤一籃子資產（例如指數），用一檔商品達成分散。',
        example: '例：買追蹤大盤的 ETF，相當於分散持有多檔成分股。'
      },
      {
        id: 3,
        title: '風險不是「一定會賠」：風險通常指波動',
        topic: '風險',
        level: 'beginner',
        content: '波動越大，短期上下越劇烈，需要更長時間或分散配置來承受。',
        example: '例：兩個資產年化都可能 6%，但波動大的那個可能中途跌很多。'
      }
    ];
    setItems(seed);
  };

  const levelLabel = (lv) => {
    const map = { beginner: '入門', intermediate: '進階', advanced: '高階' };
    return map[lv] || lv;
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((x) => {
      const matchLevel = level === 'all' || x.level === level;
      const blob = `${x.title} ${x.topic} ${x.content} ${x.example}`.toLowerCase();
      const matchQuery = !q || blob.includes(q);
      return matchLevel && matchQuery;
    });
  }, [items, query, level]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 前端 local 新增（之後你有後端再換成 API.create）
    const newItem = {
      id: Date.now(),
      ...form
    };
    setItems((prev) => [newItem, ...prev]);

    setShowModal(false);
    setForm({
      title: '',
      topic: '',
      level: 'beginner',
      content: '',
      example: ''
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>📚 金融知識</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新增知識
        </button>
      </div>

      {/* 搜尋 / 篩選區（比照你 Budget/Goals 的上方卡片區） */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜尋：複利 / ETF / 風險..."
            style={{ flex: 1, minWidth: '240px' }}
          />

          <select value={level} onChange={(e) => setLevel(e.target.value)} style={{ minWidth: '160px' }}>
            <option value="all">全部難度</option>
            <option value="beginner">入門</option>
            <option value="intermediate">進階</option>
            <option value="advanced">高階</option>
          </select>

          <div style={{ color: '#666', fontSize: '0.9rem' }}>共 {filtered.length} 則</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
        {filtered.map((k) => (
          <div key={k.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '10px', marginBottom: '10px' }}>
              <h3 style={{ margin: 0 }}>💡 {k.title}</h3>
              <span className="tag tag-income" style={{ whiteSpace: 'nowrap' }}>
                {levelLabel(k.level)}
              </span>
            </div>

            <div style={{ marginBottom: '8px', color: '#666', fontSize: '0.9rem' }}>
              主題：{k.topic || '未分類'}
            </div>

            <p style={{ color: '#444', lineHeight: 1.6 }}>
              {k.content}
            </p>

            {k.example && (
              <div className="card" style={{ background: '#fafafa' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>生活化例子</div>
                <div style={{ color: '#444', whiteSpace: 'pre-wrap' }}>{k.example}</div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: '#999' }}>
          找不到符合的知識內容，可以按「新增知識」補充。
        </div>
      )}

      {/* 新增知識 Modal（完全比照你的 Modal 結構） */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>新增金融知識</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>標題</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="例如：什麼是複利？"
                  required
                />
              </div>

              <div className="form-group">
                <label>主題</label>
                <input
                  type="text"
                  value={form.topic}
                  onChange={(e) => setForm({ ...form, topic: e.target.value })}
                  placeholder="例如：複利 / ETF / 風險"
                />
              </div>

              <div className="form-group">
                <label>難度</label>
                <select value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })}>
                  <option value="beginner">入門</option>
                  <option value="intermediate">進階</option>
                  <option value="advanced">高階</option>
                </select>
              </div>

              <div className="form-group">
                <label>內容</label>
                <textarea
                  value={form.content}
                  onChange={(e) => setForm({ ...form, content: e.target.value })}
                  placeholder="用生活化方式解釋概念..."
                  rows="4"
                  required
                />
              </div>

              <div className="form-group">
                <label>生活化例子</label>
                <textarea
                  value={form.example}
                  onChange={(e) => setForm({ ...form, example: e.target.value })}
                  placeholder="用簡單數字舉例..."
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
    </div>
  );
}

export default Learn;
