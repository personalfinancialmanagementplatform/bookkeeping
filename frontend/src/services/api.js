import axios from 'axios';

const API_BASE_URL = 'http://localhost:5005/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 帳戶 API
export const accountsAPI = {
  getAll: () => api.get('/accounts'),
  create: (data) => api.post('/accounts', data),
};

// 分類 API
export const categoriesAPI = {
    getAll: () => api.get('/categories'),
  };
  
// 交易 API
export const transactionsAPI = {
  getAll: (params) => api.get('/transactions', { params }),
  create: (data) => api.post('/transactions', data),
  delete: (id) => api.delete(`/transactions/${id}`),
  getSummary: (params) => api.get('/transactions/summary', { params }),
};

// 預算 API
export const budgetsAPI = {
  getAll: () => api.get('/budgets'),
  create: (data) => api.post('/budgets', data),
};

// 目標 API
export const goalsAPI = {
  getAll: () => api.get('/goals'),
  create: (data) => api.post('/goals', data),
  addMoney: (id, amount) => api.post(`/goals/${id}/add-money`, { amount }),
};

// 建議 API
export const suggestionsAPI = {
  get: () => api.get('/suggestions'),
};

// 新聞 API
export const newsAPI = {
  // GET /api/news/today?limit=20
  getToday: (limit = 20) => api.get('/news/today', { params: { limit } }),

  // GET /api/news/query?q=台積電&limit=20
  query: (q, limit = 20) => api.get('/news/query', { params: { q, limit } }),

  // POST /api/news/:id/summarize
  summarize: (id) => api.post(`/news/${id}/summarize`),

  // POST /api/news/ingest
  ingest: (rss_urls) => api.post('/news/ingest', { rss_urls }),
};

// 金融知識 API
export const knowledgeAPI = {
  // GET /api/knowledge?limit=50&category=投資&difficulty=入門&q=ETF
  getAll: (params = {}) => api.get('/knowledge', { params }),

  // POST /api/knowledge
  create: (data) => api.post('/knowledge', data),

  // DELETE /api/knowledge/:id
  remove: (id) => api.delete(`/knowledge/${id}`),
};
// 技術指標 API
export const technicalAPI = {
    // GET /api/technical/signals - 取得投資組合的技術訊號
    getPortfolioSignals: () => api.get('/technical/signals'),
  
    // GET /api/technical/analyze/:symbol - 分析單一股票
    analyzeStock: (symbol) => api.get(`/technical/analyze/${symbol}`),
  
    // GET /api/technical/indicators/:symbol - 取得股票技術指標數值
    getIndicators: (symbol) => api.get(`/technical/indicators/${symbol}`),
  
    // POST /api/technical/batch-analyze - 批次分析多檔股票
    batchAnalyze: (symbols) => api.post('/technical/batch-analyze', { symbols }),
  
    // GET /api/technical/watchlist-signals - 取得關注清單的技術訊號
    getWatchlistSignals: () => api.get('/technical/watchlist-signals'),
  };
  
export default api;