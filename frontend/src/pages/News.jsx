import { useEffect, useState } from 'react';
import { newsAPI } from '../services/api';

function News() {
  const [news, setNews] = useState([]);
  const [limit, setLimit] = useState(20);
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('today'); // today | search
  const [loading, setLoading] = useState(false);

  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState(null);

  const [summary, setSummary] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    loadToday();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadToday = async () => {
    setMode('today');
    setLoading(true);
    try {
      const res = await newsAPI.getToday(limit);
      setNews(res.data || []);
    } catch (e) {
      console.error('載入今日新聞失敗:', e);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e?.preventDefault?.();
    setMode('search');
    setLoading(true);
    try {
      const q = query.trim();
      const res = await newsAPI.query(q, limit);
      setNews(res.data || []);
    } catch (e) {
      console.error('搜尋新聞失敗:', e);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const openDetail = (article) => {
    setSelected(article);
    setSummary('');
    setShowModal(true);
  };

  const handleSummarize = async () => {
    if (!selected?.id) return;
    setSummaryLoading(true);
    setSummary('');
    try {
      const res = await newsAPI.summarize(selected.id);
      // 後端可能回 { summary: "..." } 或直接文字
      const s = res.data?.summary ?? (typeof res.data === 'string' ? res.data : JSON.stringify(res.data));
      setSummary(s || '');
    } catch (e) {
      console.error('摘要失敗:', e);
      setSummary('摘要產生失敗（後端 summarize 尚未完成或發生錯誤）');
    } finally {
      setSummaryLoading(false);
    }
  };

  const formatTime = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return String(iso);
    return d.toLocaleString();
  };

  const clamp = (text, n = 120) => {
    if (!text) return '';
    const t = String(text);
    return t.length > n ? t.slice(0, n) + '...' : t;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#2c3e50' }}>📰 新聞新知</h1>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <label style={{ color: '#666', fontSize: '0.9rem' }}>
            筆數
            <input
              type="number"
              min="1"
              max="100"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value || '20', 10))}
              style={{ marginLeft: '8px', width: '80px' }}
            />
          </label>
          <button className="btn btn-primary" onClick={loadToday}>
            今日新聞
          </button>
        </div>
      </div>

      {/* 搜尋列（風格比照 Budget/Goals：同樣在上方區塊） */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜尋關鍵字，例如：台積電 / 美國廠 / ETF"
            style={{ flex: 1 }}
          />
          <button className="btn btn-success" type="submit" disabled={loading}>
            🔎 搜尋
          </button>
        </form>
        <div style={{ marginTop: '10px', color: '#666', fontSize: '0.9rem' }}>
          目前模式：{mode === 'today' ? '今日新聞' : '搜尋結果'} {loading ? '（載入中...）' : `（${news.length} 則）`}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
        {news.map((a) => (
          <div key={a.id} className="card" style={{ cursor: 'pointer' }} onClick={() => openDetail(a)}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '10px' }}>
              <h3 style={{ margin: 0, lineHeight: 1.3 }}>🗞️ {a.title}</h3>
              <span className="tag tag-income" style={{ whiteSpace: 'nowrap' }}>
                {a.source || '來源'}
              </span>
            </div>

            <div style={{ marginTop: '10px', color: '#666', fontSize: '0.85rem' }}>
              發布時間：{formatTime(a.published_at)}
            </div>

            <p style={{ marginTop: '10px', color: '#444', fontSize: '0.95rem' }}>
              {clamp(a.content, 140)}
            </p>

            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openDetail(a);
              }}
            >
              查看詳情
            </button>
          </div>
        ))}
      </div>

      {news.length === 0 && !loading && (
        <div className="card" style={{ textAlign: 'center', color: '#999' }}>
          目前沒有新聞資料。你可以先按「今日新聞」或用關鍵字搜尋。
        </div>
      )}

      {/* 詳情 Modal（比照你現有 Modal 寫法） */}
      {showModal && selected && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <h3>📰 新聞詳情</h3>

            <div style={{ marginBottom: '10px' }}>
              <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{selected.title}</div>
              <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '6px' }}>
                {selected.source || '來源'} ｜ {formatTime(selected.published_at)}
              </div>
            </div>

            {/* 摘要區（可用可不用；後端沒做也不會壞） */}
            <div className="card" style={{ background: '#fafafa', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}>
                <div style={{ fontWeight: 'bold' }}>重點摘要</div>
                <button className="btn btn-success" type="button" onClick={handleSummarize} disabled={summaryLoading}>
                  {summaryLoading ? '生成中...' : '✨ 產生摘要'}
                </button>
              </div>
              <div style={{ marginTop: '10px', color: '#444', whiteSpace: 'pre-wrap' }}>
                {summary || '（尚未產生摘要）'}
              </div>
            </div>

            <div style={{ color: '#444', lineHeight: 1.6, whiteSpace: 'pre-wrap', maxHeight: '45vh', overflow: 'auto' }}>
              {selected.content || '（無內容）'}
            </div>

            <div style={{ marginTop: '12px', display: 'flex', gap: '10px' }}>
              <a className="btn" href={selected.url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
                前往原文
              </a>
              <button className="btn btn-primary" type="button" onClick={() => setShowModal(false)}>
                關閉
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default News;
