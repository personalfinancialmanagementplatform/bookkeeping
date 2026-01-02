# Financial Management Branch
# (Personal Financial Management Platform)

## Features

### 1. Daily Expense Management
- (1) Track daily and monthly spending through user-inputted expense items with real-time data updates
- (2) Automatically categorize expenses using keywords, historical data, and user habits; update spending and budget status for each category

### 2. Goal Tracking and Savings Management
- (1) Manage short-term and medium-term financial goals such as monthly savings targets and travel funds
- (2) Calculate progress toward each goal and provide clear progress reports to help users achieve their financial objectives
- (3) Generate actionable strategies based on disposable income and spending habits, offering dynamic adjustment suggestions such as increasing/decreasing weekly savings amounts

### 3. Investment Planning
- (1) Assess user risk profile and calculate monthly investable amounts; integrate financial status, spending records, savings capacity, and risk preferences to generate suitable investment portfolio allocations
- (2) Adjust recommendations based on user preferences and investment timeline, balancing both short-term and long-term planning
- (3) Provide natural language explanations for portfolio allocation rationale, making it easier for users to understand and make informed decisions
## Structure
bookkeeping/
-├── backend/
-│   ├── app/
-│   │   ├── __init__.py          # 初始化
-│   │   ├── models/              # 資料庫模型
-│   │   │   └── __init__.py
-│   │   ├── routes/              # API 
-│   │   │   └── __init__.py
-│   │   └── services/            # 業務邏輯
-│   │       └── __init__.py
-│   ├── database/                # 資料庫
-│   ├── tests/                   # 測試
-│   ├── requirements.txt         # Python套件
-│   ├── .env.example            # 環境變數範例
-│   └── README.md               # 說明文件
-├── frontend/                    # 前端
-└── research/                    # 研究筆記
