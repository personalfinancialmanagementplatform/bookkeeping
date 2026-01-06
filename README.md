# Personal Financial Management Platform
# 個人財務管理平台 - 參考 Firefly III 開源架構設計

![Version](https://img.shields.io/badge/version-1.4.2-blue)
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
| **技術指標監控** | KD 指標、MA 均線交叉訊號即時偵測與提醒 |
| **交割日計算** | 自動計算 T+2 交割日，排除週末與休市日 |
| **推薦標的資料庫** | 全部上市股票 & ETF 自動抓取、分類、篩選 |
| **配置建議** | 風險問卷評估 + 智慧投資組合配置建議 |
| **財經新聞** | 自動抓取財經新聞，AI 摘要整理 |
| **理財學習** | 理財知識庫，智慧搜尋 |
| **智慧建議** | 根據消費習慣提供動態調整建議與量化方案 |

---

## 投資組合功能

### 功能特色

| 功能 | 說明 |
|------|------|
| 持倉管理 | 新增/管理股票、ETF、債券、基金持倉 |
| 即時報價 | 串接台股即時股價（twstock）+ 美股（Yahoo Finance） |
| 資產配置 | 圓餅圖顯示各類資產占比 |
| 本月統計 | 本月投資支出、賣出收入、股息收入 |
| 最近交易 | 顯示最近 5 筆投資交易記錄 |
| 技術訊號 | 即時偵測 KD/MA 黃金交叉與死亡交叉 |
| 交割日提醒 | 賣出時自動顯示 T+2 交割日期 |
| 推薦標的 | 全部上市股票 & ETF 智慧篩選推薦 |
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

## 推薦標的資料庫功能（v1.4.2 新增）

### 功能特色

| 功能 | 說明 |
|------|------|
| 全部納入 | 從 twstock 抓取全部上市股票 & ETF（1000+ 股票、250+ ETF） |
| 自動分類 | 根據名稱/產業自動分類（20+ 種 ETF 分類、25+ 種股票產業） |
| 風險篩選 | 根據風險等級（保守/穩健/積極）自動推薦 |
| 目標篩選 | 根據投資目標（退休/成長/收益/保值）自動推薦 |
| 搜尋功能 | 支援代號、名稱、產業關鍵字搜尋 |
| 精選標的 | 另提供熱門/精選標的快速選擇 |
| 快取機制 | 24 小時快取減少重複請求 |

### 資料來源與數量

| 來源 | 資料 | 數量 |
|------|------|------|
| twstock.codes | 全部上市股票 | **約 1000+ 檔** |
| twstock.codes | 全部上市 ETF | **約 250+ 檔** |
| 自動分類 | ETF 分類 | **20+ 種** |
| 自動分類 | 股票產業 | **25+ 種** |

### ETF 自動分類

| 分類代碼 | 分類名稱 | 範例 |
|----------|----------|------|
| market_cap | 大盤型 | 0050、006208 |
| high_dividend | 高股息 | 0056、00878 |
| monthly_dividend | 月配息 | 00919、00929、00939、00940 |
| bond | 債券型 | 一般債券 ETF |
| us_bond | 美國公債 | 00679B、00687B |
| corporate_bond | 公司債 | 00720B、00751B |
| semiconductor | 半導體 | 00891、00892 |
| 5g_telecom | 5G 通訊 | 00881 |
| ev | 電動車 | 00893 |
| ai | AI 人工智慧 | AI 相關 ETF |
| financial | 金融 | 金融類 ETF |
| esg | ESG 永續 | ESG 相關 ETF |
| us_market | 美股 | 00646 |
| nasdaq | NASDAQ | 00662 |
| japan | 日本 | 日本市場 ETF |
| china | 中國 | 陸股 ETF |
| global | 全球 | 全球市場 ETF |
| low_volatility | 低波動 | 00713 |
| growth | 成長型 | 成長策略 ETF |

### 股票自動分類

| 分類代碼 | 產業名稱 |
|----------|----------|
| semiconductor | 半導體業 |
| computer | 電腦及週邊設備業 |
| optoelectronics | 光電業 |
| telecom | 通信網路業 |
| electronics | 電子零組件業 |
| it_service | 資訊服務業 |
| financial | 金融保險業 |
| food | 食品工業 |
| plastic | 塑膠工業 |
| textile | 紡織纖維 |
| machinery | 電機機械 |
| chemical | 化學工業 |
| biotech | 生技醫療業 |
| energy | 油電燃氣業 |
| steel | 鋼鐵工業 |
| automotive | 汽車工業 |
| construction | 建材營造業 |
| shipping | 航運業 |
| tourism | 觀光餐旅業 |
| retail | 貿易百貨業 |

### 風險等級推薦對照

| 風險等級 | ETF 分類 | 股票產業 |
|----------|----------|----------|
| 保守型 | 債券型、美國公債、公司債、低波動 | 金融、食品、零售 |
| 穩健型 | 大盤型、高股息、ESG、債券 | 金融、電腦、電子、通訊 |
| 積極型 | 半導體、5G、電動車、AI、NASDAQ、月配息 | 半導體、光電、生技、資訊服務 |

### 投資目標推薦對照

| 投資目標 | ETF 分類 | 股票產業 |
|----------|----------|----------|
| 退休規劃 | 高股息、月配息、債券、低波動 | 金融、食品、零售 |
| 財富增長 | 大盤型、半導體、5G、AI、NASDAQ | 半導體、光電、電腦、資訊服務 |
| 穩定收益 | 高股息、月配息、債券、公司債 | 金融、食品、能源 |
| 資產保值 | 債券、美國公債、低波動、大盤型 | 金融、食品、零售、能源 |

### 精選熱門標的

#### ETF 精選
| 分類 | 標的 | 
|------|------|
| 大盤型 | 0050 元大台灣50 |
| 大盤型 | 006208 富邦台50 | 
| 高股息 | 0056 元大高股息 |
| 高股息 | 00878 國泰永續高股息 | 
| 高股息 | 00713 元大台灣高息低波 |
| 月配息 | 00919 群益台灣精選高息 | 
| 月配息 | 00929 復華台灣科技優息 | 
| 月配息 | 00939 統一台灣高息動能 | 
| 月配息 | 00940 元大台灣價值高息 | 
| 債券 | 00679B 元大美債20年 | 
| 債券 | 00720B 元大投資級公司債 | 

#### 股票精選
| 分類 | 標的 | 
|------|------|
| 成長型 | 2330 台積電 | 
| 成長型 | 2454 聯發科 | 
| 成長型 | 2382 廣達 | 
| 金融 | 2881 富邦金 | 
| 金融 | 2882 國泰金 | 
| 金融 | 2886 兆豐金 | 
| 防禦型 | 2412 中華電 | 
| 防禦型 | 1216 統一 | 

---

## 交割日計算功能（v1.4.1 新增）

### 功能特色

| 功能 | 說明 |
|------|------|
| T+2 自動計算 | 根據賣出日期自動計算交割日 |
| 休市日排除 | 自動跳過週末與國定假日 |
| 證交所資料 | 從台灣證交所抓取官方休市日 |
| 即時提醒 | 賣出 Modal 顯示交割日期與提醒 |
| 快取機制 | 24 小時快取減少 API 請求 |

### 交割日計算規則

台股交割採用 **T+2** 制度：
- **T 日**：成交日（賣出當天）
- **T+1 日**：第一個營業日
- **T+2 日**：交割日（需款項入帳）

排除日期：
- 週六、週日
- 國定假日（元旦、春節、清明、端午、中秋、國慶等）
- 證交所公告之休市日

### 使用方式

在賣出持倉時，選擇賣出日期後會自動顯示：
- 交割日期（含星期幾）
- 跳過的假日說明
- 交割帳戶餘額提醒

---

## 技術指標監控功能（v1.4.0 新增）

### 功能特色

| 功能 | 說明 |
|------|------|
| KD 指標偵測 | 自動計算 9-3-3 KD 值，偵測黃金/死亡交叉 |
| MA 均線偵測 | 監控 5 日與 20 日均線交叉訊號 |
| 訊號強度判斷 | 區分強/普/弱訊號（超買超賣區加權） |
| 即時提醒 | 投資組合頁面卡片即時顯示買入/賣出訊號 |
| 批次分析 | 一次分析所有持倉的技術指標 |

### KD 指標交叉（隨機指標）

| 訊號類型 | 條件 | 意義 |
|----------|------|------|
| 黃金交叉 | K 線從下方往上穿過 D 線 | 短期動能增強，買入訊號 |
| 死亡交叉 | K 線從上方往下跌破 D 線 | 短期動能減弱，賣出訊號 |

**訊號強度判斷：**
- 超賣區（K < 20）出現黃金交叉 → 強烈買入訊號
- 超買區（K > 80）出現死亡交叉 → 強烈賣出訊號

### 移動平均線（MA）交叉

| 訊號類型 | 條件 | 意義 |
|----------|------|------|
| 黃金交叉 | 5 日均線向上穿過 20 日均線 | 短期趨勢轉強，看漲訊號 |
| 死亡交叉 | 5 日均線向下穿過 20 日均線 | 短期趨勢轉弱，看跌訊號 |

---

## 配置建議功能

### 功能特色

| 功能 | 說明 |
|------|------|
| 風險問卷 | 12 題金管會標準問卷評估風險承受度 |
| 風險等級 | 保守型 / 穩健型 / 積極型 三種等級 |
| 智慧配置 | 根據風險等級、投資目標、年齡自動建議資產配置 |
| 推薦標的 | 從全部上市股票 & ETF 中智慧篩選推薦 |
| 標的介紹 | 詳細說明每個推薦標的的特色與風險 |
| 下一步指引 | 提供開戶、下單等操作指引與券商資訊 |
| 快速配置 | 提供保守/平衡/成長三種預設模板 |
| 預估殖利率 | 顯示各標的預估殖利率與總體預估報酬 |

### 風險評估問卷（符合金管會標準）

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

---

## API 端點

### 基礎 API

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

### 技術指標 API（v1.4.0 新增）

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/technical/signals | 取得投資組合技術訊號 |
| GET | /api/technical/analyze/:symbol | 分析單一股票技術指標 |
| GET | /api/technical/indicators/:symbol | 取得股票 KD/MA 數值 |
| POST | /api/technical/batch-analyze | 批次分析多檔股票 |
| GET | /api/technical/watchlist-signals | 取得關注清單技術訊號 |
| GET | /api/technical/health | API 健康檢查 |

### 休市日 & 交割日 API（v1.4.1 新增）

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/holidays?year=2026 | 取得該年休市日清單 |
| GET | /api/holidays/check?date=2026-01-01 | 檢查是否為休市日 |
| GET | /api/settlement-date?sell_date=2026-01-06 | 計算 T+2 交割日 |
| POST | /api/holidays/refresh | 強制更新休市日資料 |

### 推薦標的 API（v1.4.2 新增）

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/recommendations | 取得全部股票 & ETF（1000+ 檔） |
| GET | /api/recommendations/etf?category= | 取得 ETF（可篩選分類） |
| GET | /api/recommendations/stock?sector= | 取得股票（可篩選產業） |
| GET | /api/recommendations/etf/categories | 取得 ETF 分類統計 |
| GET | /api/recommendations/stock/sectors | 取得股票產業統計 |
| GET | /api/recommendations/by-risk?level= | 根據風險等級篩選 |
| GET | /api/recommendations/by-goal?goal= | 根據投資目標篩選 |
| GET | /api/recommendations/search?q= | 搜尋全部標的 |
| GET | /api/recommendations/popular | 取得熱門/精選標的 |
| GET | /api/recommendations/statistics | 取得完整統計 |

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

### 新聞 & 知識庫 API

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | /api/news | 取得財經新聞列表 |
| GET | /api/news/:id | 取得單篇新聞詳情 |
| GET | /api/knowledge | 取得理財知識文章 |
| GET | /api/knowledge/search?q= | 搜尋知識庫 |

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
| 39 | 保險 | 🛡️ |


## 收入分類

| ID | 分類 | 圖示 |
|----|------|------|
| 9 | 薪水 | 💰 |
| 10 | 投資收益 | 📈 |
| 11 | 副業 | 💼 |
| 12 | 其他收入 | 🎁 |
| 13 | 獎金 | 🏆 |


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
- **twstock** - 台股即時報價、歷史資料、股票清單
- **requests** - HTTP 請求（Yahoo Finance API、證交所 API）
- **APScheduler** - 排程任務

### 前端 (Frontend)
- **React 18** - UI 框架
- **Vite** - 建置工具
- **React Router** - 路由管理
- **Axios** - HTTP 請求
- **Recharts** - 圖表視覺化

---

## 專案結構
```
bookkeeping/
├── backend/                 # 後端程式碼
│   ├── app/
│   │   ├── models/         # 資料模型
│   │   │   ├── news_article.py      # 新聞文章模型
│   │   │   └── knowledge_doc.py     # 知識文章模型
│   │   ├── routes/         # API 路由
│   │   │   ├── portfolio_routes.py  # 投資組合 API
│   │   │   ├── technical_routes.py  # 技術指標 API
│   │   │   ├── holiday_routes.py    # 休市日 & 交割日 API
│   │   │   ├── recommendation_routes.py # 推薦標的 API（v1.4.2 新增）
│   │   │   ├── news_routes.py       # 新聞 API
│   │   │   └── knowledge_routes.py  # 知識庫 API
│   │   ├── services/       # 業務邏輯
│   │   │   ├── stock_service.py     # 股票服務
│   │   │   ├── technical_indicator_service.py  # 技術指標服務
│   │   │   ├── holiday_service.py   # 休市日服務
│   │   │   ├── recommendation_service.py # 推薦標的服務（v1.4.2 新增）
│   │   │   ├── portfolio_advisor.py # 配置建議服務
│   │   │   ├── news_ingest_service.py    # 新聞抓取
│   │   │   ├── news_summarize_service.py # 新聞摘要
│   │   │   ├── knowledge_service.py # 知識庫服務
│   │   │   └── scheduler_service.py # 排程服務
│   │   └── utils/          # 工具函數
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
│   │   │   ├── PortfolioAdvisor.css
│   │   │   ├── TechnicalSignals.jsx    # 技術訊號組件
│   │   │   └── TechnicalSignals.css    # 技術訊號樣式
│   │   ├── pages/          # 頁面元件
│   │   │   ├── Dashboard.jsx    # 財務總覽
│   │   │   ├── Transactions.jsx # 交易記錄
│   │   │   ├── Budgets.jsx      # 預算管理
│   │   │   ├── Goals.jsx        # 財務目標
│   │   │   ├── Portfolio.jsx    # 投資組合
│   │   │   ├── Portfolio.css    # 投資組合樣式
│   │   │   ├── News.jsx         # 財經新聞
│   │   │   └── Learn.jsx        # 理財學習
│   │   ├── services/       # API 連接
│   │   │   └── api.js           # API 服務
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
- 今日持倉股票訊號監測卡片
- 持倉明細（依資產類型分組）
- 關注清單
- 配置建議按鈕

### 賣出持倉
- 賣出日期選擇
- T+2 交割日自動計算
- 跳過假日說明
- 交割帳戶餘額提醒
- 預估損益計算

### 今日持倉股票訊號監測卡片
- 買入/賣出訊號數量統計
- KD 黃金交叉/死亡交叉提醒
- MA 均線交叉提醒
- 訊號強度標示（強/普/弱）
- 一鍵重新分析

### 配置建議
- 風險問卷評估（12題金管會標準）
- 投資金額輸入（自由輸入）
- 風險偏好選擇（保守/穩健/積極）
- 投資目標選擇
- 智慧配置建議結果
- 從全部上市股票 & ETF 中智慧篩選推薦
- 推薦標的說明以及下一步動作
- 預估殖利率

### 財經新聞
- 自動抓取最新財經新聞
- AI 摘要整理

### 理財學習
- 理財知識庫
- 智慧搜尋功能

---

## 更新日誌

### v1.4.2（最新）
- 🎯 **新增完整推薦標的資料庫**
  - 從 twstock 抓取全部上市股票（1000+ 檔）
  - 從 twstock 抓取全部上市 ETF（250+ 檔）
  - ETF 自動分類（20+ 種分類）
  - 股票自動分類（25+ 種產業）
  - 根據風險等級智慧篩選推薦
  - 根據投資目標智慧篩選推薦
  - 支援關鍵字搜尋全部標的
  - 精選熱門標的快速選擇
  - 24 小時快取機制
- 🔧 **新增推薦標的 API**
  - `/api/recommendations` - 取得全部標的
  - `/api/recommendations/etf` - ETF 清單（可篩選）
  - `/api/recommendations/stock` - 股票清單（可篩選）
  - `/api/recommendations/by-risk` - 風險篩選
  - `/api/recommendations/by-goal` - 目標篩選
  - `/api/recommendations/search` - 搜尋功能
  - `/api/recommendations/popular` - 精選標的

### v1.4.1
- 🏦 新增交割日計算功能
  - 賣出時自動計算 T+2 交割日
  - 自動排除週末與國定假日
  - 從台灣證交所抓取官方休市日資料
  - 24 小時快取機制減少 API 請求
  - 賣出 Modal 顯示交割日提醒

### v1.4.0
- 📈 新增技術指標監控功能
  - KD 指標（9-3-3）自動計算與交叉偵測
  - MA 移動平均線（5日/20日）交叉偵測
  - 黃金交叉（買入訊號）與死亡交叉（賣出訊號）即時提醒
  - 訊號強度判斷（超買區/超賣區加權）
- 新增技術訊號卡片
  - 投資組合頁面新增「今日持倉股票訊號監測」
  - 顯示買入/賣出訊號統計
  - 支援展開查看所有訊號
  - 一鍵重新分析功能

### v1.3.0
- 📰 新增財經新聞功能（自動抓取、AI 摘要）
- 📚 新增理財學習知識庫
- ⏰ 新增排程服務

### v1.2.0
- 🎯 新增風險問卷評估功能（金管會 12 題標準）
- 💼 新增投資組合配置建議功能
- 新增推薦標的詳細介紹與下一步指引
- 新增 useStockData.js Hook
- 新增 RiskQuestionnaire 組件
- 新增 PortfolioAdvisor 組件
- 股票服務增強：30秒快取、限流機制、美股支援、非交易時段收盤價
- 新增配置建議相關 API 端點

### v1.1.0 
- 📊 新增投資組合功能
- 新增持倉管理、配息記錄
- 新增台股即時報價（twstock）
- 新增關注清單

### v1.0.0
- 🎉 初始版本
- 財務總覽、交易記錄、預算管理、財務目標

---

## 參考資料

- [Firefly III](https://www.firefly-iii.org/) - 開源個人財務管理系統
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [twstock](https://github.com/mlouielu/twstock) - 台灣股市資料擷取
- [台灣證券交易所](https://www.twse.com.tw/) - 休市日、股票清單資料來源

## 開發團隊

- 開發者：Jia、Tzu

## 授權

MIT License
