import { useCallback, useEffect, useState } from 'react';
import { apiGet, apiPostJson, ApiError } from '../api';
import { useAuth } from '../context/AuthContext';

const formatDate = (iso) => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return iso;
  }
};

const formatPrice = (cents, currency, interval) => {
  if (cents === 0) return 'Free';
  const value = (cents / 100).toLocaleString(undefined, { minimumFractionDigits: 2 });
  return `${currency} ${value}/${interval}`;
};

export default function SubscriptionPage() {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null); // plan name while a request is in flight
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [planData, subData] = await Promise.all([apiGet('/api/v1/subscriptions/plans'), apiGet('/api/v1/subscriptions/me')]);
      setPlans(planData);
      setSubscription(subData);
    } catch (err) {
      setError(err.message || 'Could not load subscription details');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const currentPlanName = subscription?.plan?.name;
  const isActive = subscription?.status === 'active' && !subscription?.cancel_at_period_end;

  const subscribe = async (planName) => {
    setBusy(planName);
    setError('');
    try {
      const updated = await apiPostJson('/api/v1/subscriptions/subscribe', { plan_name: planName });
      setSubscription(updated);
    } catch (err) {
      setError(err.message || 'Could not update subscription');
    } finally {
      setBusy(null);
    }
  };

  const cancel = async () => {
    setBusy('cancel');
    setError('');
    try {
      const updated = await apiPostJson('/api/v1/subscriptions/cancel', {});
      setSubscription(updated);
    } catch (err) {
      setError(err.message || 'Could not cancel subscription');
    } finally {
      setBusy(null);
    }
  };

  return (
    <section className="workspace-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Billing</p>
          <h2>Your subscription</h2>
          <p className="panel-description">
            Choose a plan to unlock more analyses.
          </p>
        </div>
        {subscription && (
          <span className={isActive ? 'mode-badge' : 'mode-badge mode-badge-muted'}>
            {subscription.plan.display_name}
            {subscription.cancel_at_period_end && ' · canceling'}
          </span>
        )}
      </div>

      {subscription && (
        <div className="sub-status">
          <div><span>Plan</span><strong>{subscription.plan.display_name}</strong></div>
          <div><span>Status</span><strong className={isActive ? 'status-active' : 'status-muted'}>{subscription.status}{subscription.cancel_at_period_end ? ' · ends at period end' : ''}</strong></div>
          <div><span>Current period</span><strong>{formatDate(subscription.current_period_start)} → {formatDate(subscription.current_period_end)}</strong></div>
        </div>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      <div className="plans-grid">
        {loading ? (
          <p className="muted">Loading plans…</p>
        ) : plans.map((plan) => {
          const isCurrent = plan.name === currentPlanName;
          const isWorking = busy === plan.name;
          return (
            <article key={plan.id} className={isCurrent ? 'plan-card plan-card-current' : 'plan-card'}>
              <div className="plan-card-head">
                <h3>{plan.display_name}</h3>
                <span className="plan-price">{formatPrice(plan.price_cents, plan.currency, plan.interval)}</span>
              </div>
              <ul className="plan-features">
                {(plan.features?.features || []).map((f) => <li key={f}>{f}</li>)}
              </ul>
              <div className="plan-actions">
                {isCurrent ? (
                  <button className="secondary-button" disabled>You're on this plan</button>
                ) : (
                  <button className="primary-button" disabled={!!busy} onClick={() => subscribe(plan.name)}>
                    {isWorking ? 'Processing…' : (plan.price_cents === 0 ? 'Switch to Free' : 'Purchase')}
                  </button>
                )}
              </div>
            </article>
          );
        })}
      </div>

      {subscription && !subscription.cancel_at_period_end && subscription.plan?.price_cents > 0 && (
        <div className="form-actions sub-cancel-row">
          <button type="button" className="secondary-button" onClick={cancel} disabled={!!busy}>
            {busy === 'cancel' ? 'Canceling…' : 'Cancel subscription'}
          </button>
        </div>
      )}
    </section>
  );
}
