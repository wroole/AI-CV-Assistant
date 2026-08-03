import React, { useCallback, useState } from 'react';
import FileDropzone from './FileDropzone';
import ProviderSelector from './ProviderSelector';
import ResultDisplay from './ResultDisplay';
import { apiPostForm } from '../api';

const API_URL = '/api/v1/analyze-resume';

export default function CandidateForm({ usage, onAnalysisComplete }) {
  const [file,setFile]=useState(null), [provider,setProvider]=useState('local'), [loading,setLoading]=useState(false), [error,setError]=useState(''), [result,setResult]=useState(null);
  const submit = useCallback(async e => { e.preventDefault(); if (!file) { setError('Choose a PDF CV first.'); return; } setLoading(true); setError(''); setResult(null); const body=new FormData(); body.append('file',file); body.append('provider',provider); try { const r = await apiPostForm(API_URL,body); setResult(r); onAnalysisComplete?.(); } catch (err) { setError(err.message); } finally { setLoading(false); } },[file,provider,onAnalysisComplete]);
  return <section className="workspace-panel">
    <div className="panel-heading"><div><p className="eyebrow">Candidate workspace</p><h2>Improve your CV</h2><p className="panel-description">Upload a resume and get a practical review of structure, ATS readiness and content.</p></div><span className="mode-badge">Candidate</span></div>
    <form onSubmit={submit}><FileDropzone id="candidate-file" label="Candidate CV" hint="PDF only, up to 10 MB" file={file} onChange={f=>{setFile(f);setError('')}} disabled={loading}/><ProviderSelector value={provider} onChange={setProvider} disabled={loading} allowsOpenai={usage?.allows_openai}/><div className="form-actions"><button className="primary-button" disabled={loading}>{loading?'Analyzing...':'Analyze CV'}</button><button type="button" className="secondary-button" onClick={()=>{setFile(null);setResult(null);setError('')}} disabled={loading||(!file&&!result)}>Clear</button></div>{error&&<div className="error" role="alert">{error}</div>}</form>
    {result&&<ResultDisplay result={result} mode="candidate" />}
  </section>;
}
