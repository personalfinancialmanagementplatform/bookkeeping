# Personal Financial Management Platform
# 個人財務管理平台 - 參考 Firefly III 開源架構設計

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Python](https://img.shields.io/badge/Python-3.13-green)
![React](https://img.shields.io/badge/React-18-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)

## 專案簡介

這是一個個人財務管理系統，幫助使用者追蹤日常收支、管理預算、設定財務目標、管理投資組合，並提供投資儲蓄智慧建議。

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

### 風險評估問卷（符合金管會）

| 題號 | 問題 |
|------|------|
| Q1 | 您的年齡層？ |
| Q2 | 您曾使用過的理財工具（可複選）？ |
| Q3 | 投資債券類型相關商品之理財工具經驗？ |
| Q4 | 投資其他非債券類型相關商品之理財工具經驗？ |
| Q5 | 下列何者最符合您對投資理財工具的理解？ |
| Q6 | 每年可用於購買投資理財工具之金額（新台幣）？ |
| Q7 | 請問您的備用金（現金及存款）相當於您幾個月的生活開銷？ |
| Q8 | 每年可承受的價格損失（含匯率風險）？ |
| Q9 | 在達到預計投資期間時（例如 3 年、5 年），可承受的價格損失？ |
| Q10 | 您的投資回報期望？ |
| Q11 | 就長期投資而言，您期望每年平均投資報酬率？ |
| Q12 | 當投資發生虧損或達到停損點時會採取的處理方式？ |

### 風險等級對照（金管會標準）

問卷共 12 題，滿分約 55 分，依得分百分比判定風險屬性：

| 等級 | 得分比例 | 適合 RR 等級 | 股票比例 | 債券比例 | 適合對象 |
|------|----------|--------------|----------|----------|----------|
| 保守型 | < 35% | RR1, RR2 | 10-20% | 40-60% | 退休族、風險承受度低者 |
| 穩健型 | 35-65% | RR1, RR2, RR3 | 35-45% | 20-30% | 一般投資人、中長期投資 |
| 積極型 | > 65% | RR1-RR5 | 55-70% | 10-15% | 年輕族群、風險承受度高者 |

**RR 風險報酬等級說明：**
- **RR1**：低風險（如貨幣市場基金）
- **RR2**：中低風險（如投資級債券）
- **RR3**：中度風險（如平衡型基金）
- **RR4**：中高風險（如股票型基金、ETF）
- **RR5**：高風險（如單一國家/產業基金、衍生性商品）

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
- **Recharts** - 圖表視覺化

---

## 專案結構
```
bookkeeping/
├── backend/                 # 後端程式碼
│   ├── app/
│   │   ├── models/         # 資料模型
│   │   ├── routes/         # API 路由
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
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bookkeeping
DB_USER=your_username
DB_PASSWORD=your_password
FLASK_ENV=development
PORT=5005
```

---

## 功能截圖

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
- 配置建議按鈕

### 配置建議
- 風險問卷評估（5題）
- 投資金額輸入（預設快捷鍵）
- 風險偏好選擇（保守/穩健/積極）
- 投資目標選擇
- 智慧配置建議結果
- 推薦標的與配置比例
- 預估殖利率

---

## 更新日誌

### v1.2.0
- 新增風險問卷評估功能
- 新增投資組合配置建議功能
- 新增 useStockData.js Hook
- 新增 RiskQuestionnaire 組件
- 新增 PortfolioAdvisor 組件
- 股票服務增強：30秒快取、限流機制、美股支援
- 新增配置建議相關 API 端點

### v1.1.0 
- 新增投資組合功能
- 新增持倉管理、配息記錄
- 新增台股即時報價（twstock）
- 新增關注清單

### v1.0.0
- 初始版本
- 財務總覽、交易記錄、預算管理、財務目標

---

## 參考資料

- [Firefly III](https://www.firefly-iii.org/) - 開源個人財務管理系統
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/)
- [twstock](https://github.com/mlouielu/twstock) - 台灣股票資料庫
- [Yahoo Finance API](https://finance.yahoo.com/)

---

## 開發團隊

開發者：Emily

---

## 授權

MIT License

---

⭐ 如果這個專案對你有幫助，請給我們一顆星！