import React, { useState } from 'react';
import CandidateForm from './components/CandidateForm';
import HRForm from './components/HRForm';
import './App.css';

export default function App() {
  const [mode, setMode] = useState('candidate');
  return <div className="App"><div className="app-shell">
    <header className="app-header"><div className="brand-lockup"><div className="brand-mark">CV</div><div><h1>AI CV Assistant</h1><p>Practical resume review for candidates and recruiters</p></div></div><span className="header-note">PDF analysis workspace</span></header>
    <nav className="tabs" aria-label="Workspace mode"><button className={mode === 'candidate' ? 'active' : ''} onClick={() => setMode('candidate')}>Candidate</button><button className={mode === 'hr' ? 'active' : ''} onClick={() => setMode('hr')}>HR / Recruiter</button></nav>
    <main>{mode === 'candidate' ? <CandidateForm /> : <HRForm />}</main>
  </div></div>;
}
