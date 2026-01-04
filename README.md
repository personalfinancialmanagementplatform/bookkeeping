# Personal Financial Management Platform
# 個人財務管理平台 - 參考 Firefly III 開源架構設計

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.13-green)
![React](https://img.shields.io/badge/React-18-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)

## 專案簡介

這是一個個人財務管理系統，幫助使用者追蹤日常收支、管理預算、設定財務目標、管理投資組合，並提供投資儲蓄智慧建議。

這是一個個人財務管理系統，幫助使用者追蹤日常收支、管理預算、設定財務目標，並提供智慧建議。

###  主要功能

| 功能 | 說明 |
|------|------|
|  **財務總覽** | 即時顯示收入、支出、結餘統計 |
|  **交易記錄** | 記錄每日收支，支援自動分類 |
|  **智慧分類** | 根據關鍵字自動分類交易 |
|  **預算管理** | 設定各類別預算，追蹤使用狀態 |
|  **財務目標** | 管理短期/中期儲蓄目標 |
|  **智慧建議** | 根據消費習慣提供動態調整建議 |

##  技術棧
## 主要功能

| 功能 | 說明 |
|------|------|
| **財務總覽** | 即時顯示收入、支出、結餘統計、儲蓄率 |
| **交易記錄** | 記錄每日收支，支援自動分類 |
| **智慧分類** | 關鍵字比對 + 金額區間自動分類 |
| **預算管理** | 設定各類別預算，自動追蹤使用狀態，過期未達標自動刪除 |
| **財務目標** | 管理短期/中期儲蓄目標，含進度追蹤（落後/如期/超前判斷） |
| **投資組合** | 股票/ETF 持倉管理、資產配置分析、即時報價 |
| **配置建議** | 風險問卷評估 + 智慧投資組合配置建議 |
| **智慧建議** | 根據消費習慣提供動態調整建議與量化方案 |

---

### 功能特色

| 功能 | 說明 |
|------|------|
| 持倉管理 | 新增/管理股票、ETF、債券、基金持倉 |
| 即時報價 | 串接台股即時股價（twstock）+ 美股（Yahoo Finance） |
| 資產配置 | 圓餅圖顯示各類資產占比 |
| 本月統計 | 本月投資支出、賣出收入、股息收入 |
| 最近交易 | 顯示最近 5 筆投資交易記錄 |
| 關注清單 | 追蹤感興趣的股票 |
| 損益計算 | 自動計算未實現損益與報酬率 |
| 配息記錄 | 追蹤股息收入與配息歷史 |

### 資產類型

| 類型 | 代碼 | 顏色 |
|------|------|------|
| 股票 | stock | 🔴 #e74c3c |
| ETF | etf | 🔵 #3498db |
| 債券 | bond | 🟢 #2ecc71 |
| 基金 | fund | 🟠 #f39c12 |

---

### 功能特色

| 功能 | 說明 |
|------|------|
| 風險問卷 | 5 題簡易問卷評估風險承受度 |
| 風險等級 | 保守型 / 穩健型 / 積極型 三種等級 |
| 智慧配置 | 根據風險等級、投資目標、年齡自動建議資產配置 |
| 推薦標的 | 推薦具體台灣 ETF、股票、債券標的 |
| 快速配置 | 提供保守/平衡/成長三種預設模板 |
| 預估殖利率 | 顯示各標的預估殖利率與總體預估報酬 |

### 風險評估問卷

| 題號 | 問題 |
|------|------|
| Q1 | 您的投資經驗有多長？ |
| Q2 | 如果投資下跌 20%，您會？ |
| Q3 | 預計這筆投資要持有多久？ |
| Q4 | 這筆投資佔總資產的比例？ |
| Q5 | 您對投資報酬的期望是？ |

### 風險等級對照

| 等級 | 分數 | 股票比例 | 債券比例 | 適合對象 |
|------|------|----------|----------|----------|
| 保守型 | 5-8 分 | 10-20% | 40-60% | 退休族、風險承受度低者 |
| 穩健型 | 9-14 分 | 35-45% | 20-30% | 一般投資人、中長期投資 |
| 積極型 | 15-20 分 | 55-70% | 10-15% | 年輕族群、風險承受度高者 |

### 投資目標

| 目標 | 說明 |
|------|------|
| 退休規劃 | 長期穩定增長，適合 10 年以上投資期 |
| 財富增長 | 追求資本增值，適合 5-10 年投資期 |
| 穩定收益 | 追求固定現金流，股息收入為主 |
| 資產保值 | 抵抗通膨，保護購買力 |

### 推薦標的資料庫

#### ETF
- 0050 元大台灣50、006208 富邦台50（大盤型）
- 0056 元大高股息、00878 國泰永續高股息（高股息）
- 00713 元大台灣高息低波（低波動）
- 00919 群益台灣精選高息、00929 復華台灣科技優息（月配息）

#### 股票
- 2330 台積電、2454 聯發科、2382 廣達（成長型）
- 2317 鴻海、2881 富邦金、2882 國泰金（穩健型）
- 1216 統一（防禦型）

#### 債券 ETF
- 00679B 元大美債20年、00687B 國泰20年美債
- 00720B 元大投資級公司債、00751B 元大AAA至A公司債

---

## API 端點

### 投資組合 API

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
| GET | /api/dividends | 取得配息記錄 |
| POST | /api/dividends | 新增配息記錄 |

### 股票服務 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/stocks/search?q= | 搜尋股票 |
| GET | /api/stocks/quote/:symbol | 取得單一即時報價 |
| POST | /api/stocks/quotes | 批次取得即時報價 |
| GET | /api/stocks/info/:symbol | 取得股票基本資訊 |
| POST | /api/holdings/refresh-prices | 更新持倉即時價格 |

### 風險評估 & 配置建議 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/risk-assessment/questions | 取得風險問卷題目 |
| POST | /api/risk-assessment/calculate | 計算風險等級 |
| POST | /api/portfolio/recommend | 取得配置建議 |
| GET | /api/portfolio/quick-recommend | 快速配置建議 |
| GET | /api/portfolio/risk-profiles | 取得風險等級說明 |
| GET | /api/portfolio/investment-goals | 取得投資目標選項 |
| GET | /api/investment/health | API 健康檢查 |

---

## 支出分類

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

## 收入分類

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

---

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
- **requests** - HTTP 請求（Yahoo Finance API）

### 前端 (Frontend)
- **React 18** - UI 框架
- **Vite** - 建置工具
- **React Router** - 路由管理
- **Axios** - HTTP 請求
- **Recharts** - 圖表視覺化

##  專案結構

```
bookkeeping/
├── backend/                 # 後端程式碼
│   ├── app/
│   │   ├── models/         # 資料模型
│   │   ├── routes/         # API 路由
│   │   └── services/       # 業務邏輯
│   │   │   └── portfolio_routes.py  # 投資組合 API（含配置建議）
│   │   └── services/
│   │       ├── stock_service.py     # 股票服務（即時報價、快取）
│   │       └── portfolio_advisor.py # 配置建議服務
│   ├── run.py              # 主程式入口
│   ├── requirements.txt    # Python 依賴
│   └── .env                # 環境變數
│
├── frontend/               # 前端程式碼
│   ├── src/
│   │   ├── pages/         # 頁面元件
│   │   ├── services/      # API 連接
│   │   ├── App.jsx        # 主應用程式
│   │   └── App.css        # 樣式
│   │   ├── hooks/          # 自訂 Hooks
│   │   │   └── useStockData.js     # 股票數據 Hook
│   │   ├── components/     # 共用組件
│   │   │   ├── RiskQuestionnaire.jsx   # 風險問卷組件
│   │   │   ├── RiskQuestionnaire.css
│   │   │   ├── PortfolioAdvisor.jsx    # 配置建議組件
│   │   │   └── PortfolioAdvisor.css
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # 財務總覽
│   │   │   ├── Transactions.jsx # 交易記錄
│   │   │   ├── Budgets.jsx      # 預算管理
│   │   │   ├── Goals.jsx        # 財務目標
│   │   │   ├── Portfolio.jsx    # 投資組合（含配置建議）
│   │   │   └── Portfolio.css
│   │   ├── App.jsx         # 主應用程式
│   │   └── App.css         # 樣式
│   └── package.json
│
└── README.md
```

##  快速開始

### 前置需求

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### 1. Clone 專案

```bash
git clone https://github.com/personalfinancialmanagementplatform/bookkeeping.git
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

##  API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/accounts` | 取得所有帳戶 |
| POST | `/api/accounts` | 建立新帳戶 |
| GET | `/api/categories` | 取得所有分類 |
| GET | `/api/transactions` | 取得交易記錄 |
| POST | `/api/transactions` | 建立交易（自動分類）|
| GET | `/api/transactions/summary` | 取得收支摘要 |
| GET | `/api/budgets` | 取得預算列表 |
| POST | `/api/budgets` | 建立新預算 |
| GET | `/api/goals` | 取得財務目標 |
| POST | `/api/goals` | 建立新目標 |
| POST | `/api/goals/:id/add-money` | 存入金額 |
| GET | `/api/suggestions` | 取得智慧建議 |


### 財務總覽
- 本月收入/支出/結餘統計
- 支出分類圓餅圖
- 智慧建議面板

### 交易記錄
- 交易列表（日期、說明、分類、金額）
- 新增交易表單
- 自動分類功能

### 預算管理
- 預算卡片（進度條顯示使用率）
- 超支/警告狀態提示

### 財務目標
- 目標進度追蹤
- 存入金額功能
- 優先級與截止日期

##  環境變數

## 環境變數

在 `backend/.env` 設定：
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookkeeping
DB_USER=your_username
DB_PASSWORD=your_password
FLASK_ENV=development
PORT=5005
```

## 📚 參考資料

- [Firefly III](https://github.com/firefly-iii/firefly-iii) - 開源個人財務管理系統
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)

##  開發團隊

- 開發者：Emily

##  授權

MIT License

---

如果這個專案對你有幫助，請給我們一顆星！
