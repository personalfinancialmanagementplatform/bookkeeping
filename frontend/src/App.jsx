import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Budgets from './pages/Budgets';
import Goals from './pages/Goals';
import Portfolio from './pages/Portfolio';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        {/* 側邊欄 */}
        <nav className="sidebar">
          <div className="logo">
            <h2>💰 財務管理</h2>
          </div>
          <ul className="nav-links">
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                📊 總覽
              </NavLink>
            </li>
            <li>
              <NavLink to="/transactions" className={({ isActive }) => isActive ? 'active' : ''}>
                📝 交易記錄
              </NavLink>
            </li>
            <li>
              <NavLink to="/budgets" className={({ isActive }) => isActive ? 'active' : ''}>
                💵 預算管理
              </NavLink>
            </li>
            <li>
              <NavLink to="/goals" className={({ isActive }) => isActive ? 'active' : ''}>
                🎯 財務目標
              </NavLink>
            </li>
            <li>
              <NavLink to="/portfolio" className={({ isActive }) => isActive ? 'active' : ''}>
                📈 投資組合
              </NavLink>
            </li>
          </ul>
        </nav>

        {/* 主要內容 */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/budgets" element={<Budgets />} />
            <Route path="/goals" element={<Goals />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;