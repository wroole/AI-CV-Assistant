import { useCallback, useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import CandidateForm from '../components/CandidateForm';
import HRForm from '../components/HRForm';
import UsageBadge from '../components/UsageBadge';
import { apiGet } from '../api';

export default function AnalyzePage() {
  const { mode } = useOutletContext() || {};
  const [usage, setUsage] = useState(null);

  const loadUsage = useCallback(async () => {
    try {
      setUsage(await apiGet('/api/v1/usage/me'));
    } catch {
      setUsage(null);
    }
  }, []);

  useEffect(() => { loadUsage(); }, [loadUsage]);

  const handleAnalysisComplete = useCallback(() => { loadUsage(); }, [loadUsage]);

  return (
    <>
      <UsageBadge usage={usage} />
      {mode === 'hr'
        ? <HRForm usage={usage} onAnalysisComplete={handleAnalysisComplete} />
        : <CandidateForm usage={usage} onAnalysisComplete={handleAnalysisComplete} />}
    </>
  );
}
