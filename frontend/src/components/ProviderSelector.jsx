import React from 'react';

export default function ProviderSelector({ value, onChange, disabled, allowsOpenai = true }) {
  return <fieldset className="provider-field" disabled={disabled}>
    <legend>Analysis provider</legend>
    <div className="provider-switch">
      <label className={value === 'local' ? 'provider-option active' : 'provider-option'}><input type="radio" name="provider" value="local" checked={value === 'local'} onChange={e => onChange(e.target.value)} /><span><strong>Local</strong><small>Ollama on this machine</small></span></label>
      <label className={`provider-option ${value === 'api' ? 'active' : ''} ${allowsOpenai ? '' : 'provider-option-locked'}`}>
        <input type="radio" name="provider" value="api" checked={value === 'api'} onChange={e => onChange(e.target.value)} disabled={disabled || !allowsOpenai} />
        <span><strong>OpenAI API</strong><small>{allowsOpenai ? 'Uses your configured API key' : 'Upgrade to Pro to unlock'}</small></span>
      </label>
    </div>
  </fieldset>;
}
