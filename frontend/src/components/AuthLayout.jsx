export default function AuthLayout({ children }) {
  return (
    <div className="auth-screen">
      <div className="auth-card-wrapper">
        <div className="brand-lockup auth-brand">
          <div>
            <h1>AI CV Assistant</h1>
            <p>Practical resume review for candidates and recruiters</p>
          </div>
        </div>
        <div className="workspace-panel auth-panel">{children}</div>
      </div>
    </div>
  );
}
