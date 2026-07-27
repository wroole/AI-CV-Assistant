import React from 'react';

export default function ProviderSelector({ value, onChange, disabled }) {
  return <fieldset className="provider-field" disabled={disabled}>
    <legend>Analysis provider</legend>
    <div className="provider-switch">
      <label className={value === 'local' ? 'provider-option active' : 'provider-option'}><input type="radio" name="provider" value="local" checked={value === 'local'} onChange={e => onChange(e.target.value)} /><span><strong>Local</strong><small>Ollama on this machine</small></span></label>
      <label className={value === 'api' ? 'provider-option active' : 'provider-option'}><input type="radio" name="provider" value="api" checked={value === 'api'} onChange={e => onChange(e.target.value)} /><span><strong>OpenAI API</strong><small>Uses your configured API key</small></span></label>
    </div>
  </fieldset>;
}
