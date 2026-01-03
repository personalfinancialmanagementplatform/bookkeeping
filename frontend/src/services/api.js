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

export default api;