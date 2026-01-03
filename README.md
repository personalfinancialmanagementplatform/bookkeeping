# Personal Financial Management Platform

個人財務管理平台 - 參考 Firefly III 開源架構設計

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13-green.svg)
![React](https://img.shields.io/badge/React-18.x-61dafb.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)

##  專案簡介

這是一個個人財務管理系統，幫助使用者追蹤日常收支、管理預算、設定財務目標、管理投資組合，並提供智慧建議。


###  主要功能

| 功能 | 說明 |
|------|------|
| **財務總覽** | 即時顯示收入、支出、結餘統計、儲蓄率 |
| **交易記錄** | 記錄每日收支，支援自動分類 |
| **智慧分類** | 關鍵字比對 + 金額區間自動分類 |
| **預算管理** | 設定各類別預算，自動追蹤使用狀態，過期未達標自動刪除 |
| **財務目標** | 管理短期/中期儲蓄目標，含進度追蹤（落後/如期/超前判斷） |
| **投資組合** | 股票/ETF 持倉管理、資產配置分析、即時報價 |
| **智慧建議** | 根據消費習慣提供動態調整建議與量化方案 |
---

## 📈 投資組合功能（v1.1 新增）

### 功能特色
| 功能 | 說明 |
|------|------|
| 持倉管理 | 新增/管理股票、ETF、債券、基金持倉 |
| 即時報價 | 串接台股即時股價（twstock） |
| 資產配置 | 圓餅圖顯示各類資產占比 |
| 本月統計 | 本月投資支出、賣出收入、股息收入 |
| 最近交易 | 顯示最近 5 筆投資交易記錄 |
| 關注清單 | 追蹤感興趣的股票 |
| 損益計算 | 自動計算未實現損益與報酬率 |

### 資產類型
| 類型 | 代碼 | 顏色 |
|------|------|------|
| 股票 | stock | 🔴 #e74c3c |
| ETF | etf | 🔵 #3498db |
| 債券 | bond | 🟢 #2ecc71 |
| 基金 | fund | 🟠 #f39c12 |

### 投資 API 端點
| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/investment-accounts | 取得投資帳戶 |
| POST | /api/investment-accounts | 建立投資帳戶 |
| GET | /api/holdings | 取得所有持倉 |
| POST | /api/holdings | 新增持倉（買入） |
| POST | /api/holdings/:id/sell | 賣出持倉 |
| GET | /api/portfolio/summary | 投資組合摘要 |
| GET | /api/portfolio/monthly-stats | 本月投資統計 |
| GET | /api/watchlist | 取得關注清單 |
| POST | /api/watchlist | 新增關注 |
| DELETE | /api/watchlist/:id | 移除關注 |
| GET | /api/stocks/search?q= | 搜尋股票 |
| GET | /api/stocks/quote/:symbol | 取得即時報價 |

---

## 📁 支出分類
| ID | 分類 | 圖示 |
|----|------|------|
| 1 | 食物飲料 | 🍔 |
| 2 | 交通 | 🚗 |
| 3 | 購物 | 🛍️ |
| 4 | 娛樂 | 🎬 |
| 5 | 帳單 | 💡 |
| 6 | 醫療 | 🏥 |
| 7 | 教育 | 📚 |
| 8 | 其他支出 | 📦 |
| 37 | 生活必需 | 🏠 |
| 38 | 投資支出 | 📊 |

## 💰 收入分類
| ID | 分類 | 圖示 |
|----|------|------|
| 9 | 薪水 | 💰 |
| 10 | 投資收益 | 📈 |
| 11 | 副業 | 💼 |
| 12 | 其他收入 | 🎁 |

---

## 自動分類邏輯
系統依照以下優先順序自動分類交易：

1. **關鍵字比對** - 根據交易描述中的關鍵字判斷
2. **金額區間** - 當關鍵字無法判斷時，依金額範圍推測
   - $20-80 → 食物飲料（飲料、小點心）
   - $80-200 → 食物飲料（正餐）
   - $15-50 → 交通（捷運、公車）

## 目標進度判斷
| 狀態 | 條件 | 建議 |
|------|------|------|
| behind 落後 | 進度 < 預期 80% | 增加儲蓄或延長期限 |
| on_track 如期 | 進度 80% - 120% | 保持現有策略 |
| ahead 超前 | 進度 > 預期 120% | 可提前完成或獎勵自己 |

---

## 技術棧

### 後端 (Backend)
- **Python 3.13** - 主程式語言
- **Flask 3.1** - Web 框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL 15** - 資料庫
- **Flask-CORS** - 跨域支援
- **twstock** - 台股即時報價

### 前端 (Frontend)
- **React 18** - UI 框架
- **Vite** - 建置工具
- **React Router** - 路由管理
- **Recharts** - 圖表視覺化

---

## 專案結構
```
bookkeeping/
├── backend/                 # 後端程式碼
│   ├── app/
│   │   ├── models/         # 資料模型
│   │   ├── routes/         # API 路由
│   │   │   └── portfolio_routes.py  # 投資組合 API
│   │   └── services/
│   │       └── stock_service.py     # 股票服務
│   ├── run.py              # 主程式入口
│   ├── requirements.txt    # Python 依賴
│   └── .env                # 環境變數
│
├── frontend/               # 前端程式碼
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # 財務總覽
│   │   │   ├── Transactions.jsx # 交易記錄
│   │   │   ├── Budget.jsx       # 預算管理
│   │   │   ├── Goals.jsx        # 財務目標
│   │   │   └── Portfolio.jsx    # 投資組合 ⭐ NEW
│   │   ├── App.jsx        # 主應用程式
│   │   └── App.css        # 樣式
│   └── package.json
│
└── README.md
```

---

## 快速開始

### 前置需求
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### 1. Clone 專案
```bash
git clone https://github.com/emily200008/bookkeeping.git
cd bookkeeping
```

### 2. 設定資料庫
```sql
-- 在 PostgreSQL 建立資料庫
CREATE DATABASE bookkeeping;
```

### 3. 啟動後端
```bash
cd backend

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的資料庫設定

# 啟動伺服器
python run.py
```
後端將在 http://localhost:5005 運行

### 4. 啟動前端
```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```
前端將在 http://localhost:5173 運行

---

## 環境變數
在 `backend/.env` 設定：
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookkeeping
DB_USER=your_username
DB_PASSWORD=your_password
FLASK_ENV=development
PORT=5005
```

---

## 功能

### 財務總覽
- 本月收入/支出/結餘統計
- 支出分類圓餅圖
- 智慧建議面板

### 投資組合
- 本月投資支出/賣出收入/股息收入
- 總市值與未實現損益
- 資產配置圓餅圖
- 最近交易記錄
- 持倉明細（依資產類型分組）
- 關注清單

---

## 參考資料
- [Firefly III](https://www.firefly-iii.org/) - 開源個人財務管理系統
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [twstock](https://github.com/mlouielu/twstock) - 台灣股票資料庫

---

## 開發團隊
- **開發者**：Emily

## 授權
MIT License

---

⭐如果這個專案對你有幫助，請給我們一顆星！