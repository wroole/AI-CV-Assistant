import React, { useRef, useState } from 'react';

export default function FileDropzone({ id, label, hint, file, onChange, disabled }) {
  const input = useRef(null);
  const [dragging, setDragging] = useState(false);
  const pick = f => { if (f && f.name.toLowerCase().endsWith('.pdf')) onChange(f); };
  return <div className="field">
    <label className="field-label" htmlFor={id}>{label}</label>
    <div className={'file-dropzone ' + (dragging ? 'is-dragging ' : '') + (file ? 'has-file' : '')}
      onDragOver={e => { e.preventDefault(); if (!disabled) setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); if (!disabled) pick(e.dataTransfer.files[0]); }}>
      <input ref={input} id={id} className="visually-hidden" type="file" accept=".pdf,application/pdf" disabled={disabled} onChange={e => pick(e.target.files[0])} />
      <div className="upload-mark">PDF</div>
      <div className="dropzone-copy"><strong>{file ? file.name : 'Drop a PDF here'}</strong><span>{file ? (file.size / 1024 / 1024).toFixed(2) + ' MB selected' : hint}</span></div>
      <button type="button" className="secondary-button choose-button" onClick={() => input.current?.click()} disabled={disabled}>{file ? 'Change file' : 'Choose PDF'}</button>
    </div>
    {file && <div className="selected-file"><span>Selected: {file.name}</span><button type="button" className="text-button" onClick={() => onChange(null)} disabled={disabled}>Remove</button></div>}
  </div>;
}
