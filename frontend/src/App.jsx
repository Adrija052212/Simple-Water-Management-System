
import { BrowserRouter, NavLink, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import './App.css'
import Consumption from './pages/Consumption'
import Prediction from './pages/Prediction'
import Optimization from './pages/Optimization'
import Dashboard from './pages/Dashboard'


const navigation = [
  { name: 'Dashboard', path: '/dashboard', icon: '▦' },
  { name: 'Consumption', path: '/consumption', icon: '◉' },
  { name: 'Prediction', path: '/prediction', icon: '⌁' },
  { name: 'Optimization', path: '/optimization', icon: '◇' },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">A</div>
        <div>
          <h2>AquaSense</h2>
          <span>WATER MANAGEMENT</span>
        </div>
      </div>

      <div className="nav-label">WORKSPACE</div>

      <nav className="navigation">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-icon">{item.icon}</span>
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="water-tip">
          <span className="tip-icon">💧</span>
          <h3>Every drop counts.</h3>
          <p>Understand your usage. Make smarter water decisions.</p>
        </div>
        <div className="sidebar-footer">Smart Water Consumption System</div>
      </div>
    </aside>
  )
}

function Header() {
  const location = useLocation()
  const currentPage = navigation.find(
    (item) => item.path === location.pathname
  )

  return (
    <header className="topbar">
      <div>
        <span className="breadcrumb">AquaSense / </span>
        <span className="current-page">
          {currentPage?.name || 'Dashboard'}
        </span>
      </div>
      <div className="header-right">
        <span className="system-status">
          <span className="status-dot"></span>
          System online
        </span>
        <div className="profile-avatar">U</div>
      </div>
    </header>
  )
}


function PlaceholderPage({ title, description, number }) {
  return (
    <div className="page-content">
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE / {title.toUpperCase()}</p>
          <h1>{title}</h1>
          <p className="page-description">{description}</p>
        </div>
      </div>
      <section className="panel placeholder-panel">
        <div className="placeholder-number">{number}</div>
        <h2>{title} module</h2>
        <p>
          This section will be implemented next and connected to the Flask backend.
        </p>
      </section>
    </div>
  )
}

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-area">
        <Header />
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route
            path="/consumption"
            element={
              <Consumption/>}/>
          <Route
            path="/prediction"
            element={
              <Prediction/>}/>
          <Route
            path="/optimization"
            element={
              <Optimization/>}/>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  )
}

export default App
