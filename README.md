# Personal Financial Management Platform

個人財務管理平台 - 參考 Firefly III 開源架構設計

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13-green.svg)
![React](https://img.shields.io/badge/React-18.x-61dafb.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)

##  專案簡介

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

### 後端 (Backend)
- **Python 3.13** - 主程式語言
- **Flask 3.1** - Web 框架
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL 15** - 資料庫
- **Flask-CORS** - 跨域支援

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
