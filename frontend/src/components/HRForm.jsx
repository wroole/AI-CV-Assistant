import React, { useCallback, useState } from 'react';
import FileDropzone from './FileDropzone';
import ProviderSelector from './ProviderSelector';
import ResultDisplay from './ResultDisplay';
import { apiPostForm } from '../api';

const API_URL = '/api/v1/hr/analyze-candidate';

export default function HRForm({ usage, onAnalysisComplete }) {
  const [file,setFile]=useState(null), [source,setSource]=useState('text'), [jdText,setJdText]=useState(''), [jdUrl,setJdUrl]=useState(''), [jdFile,setJdFile]=useState(null), [provider,setProvider]=useState('local'), [loading,setLoading]=useState(false), [error,setError]=useState(''), [result,setResult]=useState(null);
  const submit=useCallback(async e=>{e.preventDefault();if(!file){setError('Choose a candidate PDF first.');return;}if(source==='text'&&!jdText.trim()){setError('Add the job description text first.');return;}if(source==='url'&&!jdUrl.trim()){setError('Add a public job URL first.');return;}if(source==='pdf'&&!jdFile){setError('Choose a job description PDF first.');return;}setLoading(true);setError('');setResult(null);const body=new FormData();body.append('file',file);body.append('provider',provider);if(source==='text')body.append('job_description',jdText);if(source==='url')body.append('job_description_url',jdUrl);if(source==='pdf')body.append('job_description_file',jdFile);try{const r=await apiPostForm(API_URL,body);setResult(r);onAnalysisComplete?.();}catch(err){setError(err.message);}finally{setLoading(false);}},[file,source,jdText,jdUrl,jdFile,provider,onAnalysisComplete]);
  const clear=()=>{setFile(null);setSource('text');setJdText('');setJdUrl('');setJdFile(null);setResult(null);setError('');};
  return <section className="workspace-panel"><div className="panel-heading"><div><p className="eyebrow">Recruiting workspace</p><h2>Compare a candidate</h2><p className="panel-description">Use pasted text, a public job URL or a PDF to assess candidate fit.</p></div><span className="mode-badge">HR</span></div>
    <form onSubmit={submit}><FileDropzone id="hr-candidate-file" label="Candidate CV" hint="PDF only, up to 10 MB" file={file} onChange={f=>{setFile(f);setError('')}} disabled={loading}/><fieldset className="source-field"><legend>Job description source</legend><div className="source-tabs">{[['text','Paste text'],['url','Public URL'],['pdf','Upload PDF']].map(([value,label])=><button type="button" key={value} className={source===value?'source-tab active':'source-tab'} onClick={()=>{setSource(value);setError('')}} disabled={loading}>{label}</button>)}</div></fieldset>
    {source==='text'&&<div className="field"><label className="field-label" htmlFor="jd-text">Job description</label><textarea id="jd-text" value={jdText} onChange={e=>setJdText(e.target.value)} placeholder="Paste the role, requirements and responsibilities..." disabled={loading}/></div>}
    {source==='url'&&<div className="field"><label className="field-label" htmlFor="jd-url">Public job URL</label><input id="jd-url" type="url" value={jdUrl} onChange={e=>setJdUrl(e.target.value)} placeholder="https://example.com/jobs/data-analyst" disabled={loading}/><p className="field-hint">The server extracts visible text from the public page. Login-only pages may not work.</p></div>}
    {source==='pdf'&&<FileDropzone id="job-description-file" label="Job description PDF" hint="PDF only, up to 10 MB" file={jdFile} onChange={f=>{setJdFile(f);setError('')}} disabled={loading}/>}
    <ProviderSelector value={provider} onChange={setProvider} disabled={loading} allowsOpenai={usage?.allows_openai}/><div className="form-actions"><button className="primary-button" disabled={loading}>{loading?'Analyzing...':'Analyze candidate'}</button><button type="button" className="secondary-button" onClick={clear} disabled={loading||(!file&&!result)}>Clear</button></div>{error&&<div className="error" role="alert">{error}</div>}</form>
    {result&&<ResultDisplay result={result} mode="hr" />}
  </section>;
}
