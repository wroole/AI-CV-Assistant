import { useState } from 'react';
import { NavLink, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import './App.css';

export default function App() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('candidate');
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="App">
      <div className="app-shell">
        <header className="app-header">
          <div className="brand-lockup">
            <div>
              <h1>AI CV Assistant</h1>
              <p>Practical resume review for candidates and recruiters</p>
            </div>
          </div>
          <div className="header-right">
            {user && (
              <span className="header-user" title={user.email}>{user.full_name || user.email}</span>
            )}
            <button type="button" className="text-button header-logout" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        </header>

        <nav className="app-nav" aria-label="Primary">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Analyze</NavLink>
          <NavLink to="/subscription" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Subscription</NavLink>
        </nav>

        {location.pathname === '/' && (
          <nav className="tabs" aria-label="Workspace mode">
            <button className={mode === 'candidate' ? 'active' : ''} onClick={() => setMode('candidate')}>Candidate</button>
            <button className={mode === 'hr' ? 'active' : ''} onClick={() => setMode('hr')}>HR / Recruiter</button>
          </nav>
        )}

        <main>
          <Outlet context={{ mode, setMode }} />
        </main>
      </div>
    </div>
  );
}
