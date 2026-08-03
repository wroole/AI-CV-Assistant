import { Link } from 'react-router-dom';

export default function UsageBadge({ usage }) {
  if (!usage) return null;

  const { plan_name, limit, remaining, unlimited } = usage;
  const empty = !unlimited && remaining === 0;

  return (
    <div className={empty ? 'usage-badge usage-empty' : 'usage-badge'}>
      <span className="usage-dot" />
      {unlimited ? (
        <span><strong>Unlimited analyses</strong>{plan_name ? ` · ${plan_name}` : ''}</span>
      ) : empty ? (
        <span><strong>No analyses left</strong> this period — <Link to="/subscription">upgrade your plan</Link></span>
      ) : (
        <span>
          <strong>{remaining}</strong> {remaining === 1 ? 'analysis' : 'analyses'} left this period
          {limit ? <em> of {limit}</em> : null}
        </span>
      )}
    </div>
  );
}
