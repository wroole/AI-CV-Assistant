import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/AuthLayout';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(email, password, fullName);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Could not create account');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-heading">
        <p className="eyebrow">Get started</p>
        <h2>Create your account</h2>
        <p className="panel-description auth-sub">
          Sign up to analyze CVs and unlock the full workspace. Every new account starts on the Free plan.
        </p>
      </div>
      <form onSubmit={submit} className="auth-form">
        <div className="field">
          <label className="field-label" htmlFor="register-name">Full name <span className="field-optional">(optional)</span></label>
          <input id="register-name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} autoComplete="name" disabled={submitting} placeholder="Jane Doe" />
        </div>
        <div className="field">
          <label className="field-label" htmlFor="register-email">Email</label>
          <input id="register-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" disabled={submitting} placeholder="you@example.com" />
        </div>
        <div className="field">
          <label className="field-label" htmlFor="register-password">Password</label>
          <input id="register-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="new-password" disabled={submitting} placeholder="At least 8 characters" />
          <p className="field-hint">Use at least 8 characters.</p>
        </div>
        {error && <div className="error" role="alert">{error}</div>}
        <div className="form-actions">
          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </div>
      </form>
      <p className="auth-switch">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  );
}
