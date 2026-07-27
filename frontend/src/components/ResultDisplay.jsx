import React, { useMemo } from 'react';

const clampScore = (value) => {
  const numeric = Number(value ?? 0);
  if (Number.isNaN(numeric)) return 0;
  return Math.max(0, Math.min(100, numeric));
};

const asArray = (value) => (Array.isArray(value) ? value.filter(Boolean) : []);

const getScoreTone = (score) => {
  const normalized = clampScore(score);
  if (normalized >= 80) return 'good';
  if (normalized >= 60) return 'warning';
  return 'danger';
};

const formatRecommendation = (value) => {
  if (!value) return '';
  return String(value).replace(/_/g, ' ').toUpperCase();
};

const ResultDisplay = ({ result, mode }) => {
  const basicScores = result?.basic_scores || {};
  const basicDetails = basicScores.details || {};
  const resumeFeatures = result?.resume_features || {};
  const analysis = result?.analysis || {};
  const isCandidate = mode === 'candidate';

  const heroScore = clampScore(
    isCandidate ? analysis.overall_score ?? basicScores.total_score : analysis.candidate_fit_score ?? basicScores.total_score
  );
  const heroTone = getScoreTone(heroScore);

  const scoreMetrics = useMemo(() => {
    if (isCandidate) {
      return [
        ['Overall', analysis.overall_score],
        ['ATS', analysis.ats_score],
        ['Grammar', analysis.grammar_score],
        ['Structure', analysis.structure_score],
        ['Skills', analysis.skills_score],
      ];
    }

    return [
      ['Fit', analysis.candidate_fit_score],
      ['Skills match', analysis.skills_match_score],
      ['Experience', analysis.experience_match_score],
      ['Risk', analysis.risk_score],
    ];
  }, [analysis, isCandidate]);

  const strengths = asArray(analysis.strengths).slice(0, 5);
  const problems = asArray(isCandidate ? analysis.problems : analysis.concerns);
  const recommendations = asArray(analysis.recommendations);
  const interviewQuestions = asArray(analysis.interview_questions);
  const matchedSkills = asArray(analysis.matched_skills);
  const missingRequiredSkills = asArray(analysis.missing_required_skills);
  const missingNiceSkills = asArray(analysis.missing_nice_to_have_skills);
  const hasSkillsData = matchedSkills.length > 0 || missingRequiredSkills.length > 0 || missingNiceSkills.length > 0;

  if (!result) return null;

  const missingInfo = [
    !(analysis.has_email ?? resumeFeatures.has_email) && 'Email address',
    !(analysis.has_phone ?? resumeFeatures.has_phone) && 'Phone number',
    !(analysis.has_linkedin ?? resumeFeatures.has_linkedin) && 'LinkedIn profile',
    !(analysis.has_github ?? resumeFeatures.has_github) && 'GitHub profile',
    (analysis.word_count ?? resumeFeatures.word_count ?? 0) < 200 &&
      `More detailed content (${analysis.word_count ?? resumeFeatures.word_count ?? 0} words now)`,
    (analysis.bullet_count ?? resumeFeatures.bullet_count ?? 0) < 5 &&
      `More achievement bullets (${analysis.bullet_count ?? resumeFeatures.bullet_count ?? 0} now)`,
  ].filter(Boolean);

  const renderScoreMetric = ([label, value]) => {
    const score = clampScore(value);
    const tone = getScoreTone(label === 'Risk' ? 100 - score : score);

    return (
      <div className={`metric-card tone-${tone}`} key={label}>
        <div className="metric-topline">
          <span>{label}</span>
          <strong>{score}/100</strong>
        </div>
        <div className="metric-track" aria-hidden="true">
          <span style={{ width: `${score}%` }} />
        </div>
      </div>
    );
  };

  const renderList = (items, className = 'insight-list') => (
    <ul className={className}>
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>{item}</li>
      ))}
    </ul>
  );

  return (
    <section className={`results results-${mode}`}>
      <div className="results-hero">
        <div className="results-title-block">
          <p className="eyebrow">{isCandidate ? 'Report' : 'Hiring report'}</p>
          <h3>{isCandidate ? 'CV analysis' : 'Candidate fit analysis'}</h3>
          <p>
            {isCandidate
              ? 'A structured review of resume quality, ATS readiness and missing profile signals.'
              : 'A hiring-focused view of fit, matching evidence, risks and interview follow-up.'}
          </p>
        </div>
        <div className={`hero-score tone-${heroTone}`} aria-label={`Score ${heroScore} out of 100`}>
          <div className="score-ring" style={{ '--score': heroScore }}>
            <strong>{heroScore}</strong>
            <span>/100</span>
          </div>
          <small>{isCandidate ? 'Overall score' : 'Fit score'}</small>
        </div>
        <span className="result-provider">{result.provider}</span>
      </div>

      <article className="result-card analysis-card">
        <div className="result-card-header">
          <div>
            <span className="eyebrow">{isCandidate ? 'Professional review' : 'HR analysis'}</span>
            <h4>{isCandidate ? 'Resume performance' : 'Hiring decision signals'}</h4>
          </div>
          {analysis.recommendation && (
            <span className={`recommendation-badge recommendation-${analysis.recommendation}`}>
              {formatRecommendation(analysis.recommendation)}
            </span>
          )}
        </div>

        <div className="score-overview">{scoreMetrics.map(renderScoreMetric)}</div>

        {!isCandidate && (analysis.detected_job_title || analysis.detected_seniority) && (
          <div className="section job-info-panel">
            <h4>Detected Job Information</h4>
            <div className="job-info-grid">
              <p><span>Position</span><strong>{analysis.detected_job_title || 'Not specified'}</strong></p>
              <p><span>Seniority</span><strong>{analysis.detected_seniority || 'Not specified'}</strong></p>
            </div>
          </div>
        )}

        <div className="insight-grid">
          {strengths.length > 0 && (
            <section className="section insight-panel panel-positive">
              <h4>Strengths</h4>
              {renderList(strengths)}
            </section>
          )}

          {problems.length > 0 && (
            <section className="section insight-panel panel-warning">
              <h4>{isCandidate ? 'Issues Found' : 'Concerns'}</h4>
              <ul className="issue-list">
                {problems.map((item, index) => (
                  <li key={`${item}-${index}`}>
                    <span>{item}</span>
                    <strong>Medium</strong>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {isCandidate && recommendations.length > 0 && (
          <section className="section action-panel">
            <h4>How to Improve</h4>
            <ol className="numbered-list">
              {recommendations.map((item, index) => (
                <li key={`${item}-${index}`}>{item}</li>
              ))}
            </ol>
          </section>
        )}

        {isCandidate && (
          <section className="section insight-panel">
            <h4>Missing Information</h4>
            {missingInfo.length > 0 ? renderList(missingInfo, 'tag-list') : <p className="missing-info-none">All key information sections are present.</p>}
          </section>
        )}

        {isCandidate && analysis.improved_summary && (
          <section className="section summary-panel">
            <h4>Recruiter Summary</h4>
            <p>{analysis.improved_summary}</p>
          </section>
        )}

        {!isCandidate && interviewQuestions.length > 0 && (
          <section className="section action-panel">
            <h4>Suggested Interview Questions</h4>
            <ol className="numbered-list">
              {interviewQuestions.map((item, index) => (
                <li key={`${item}-${index}`}>{item}</li>
              ))}
            </ol>
          </section>
        )}

        {!isCandidate && analysis.short_hr_summary && (
          <section className="section summary-panel">
            <h4>HR Summary</h4>
            <p>{analysis.short_hr_summary}</p>
          </section>
        )}

        {!isCandidate && hasSkillsData && (
          <section className="section skills-panel">
            <h4>Skills Match Analysis</h4>
            <div className="skills-columns">
              {matchedSkills.length > 0 && (
                <div>
                  <h5>Matched Skills</h5>
                  {renderList(matchedSkills, 'tag-list tag-list-positive')}
                </div>
              )}
              {missingRequiredSkills.length > 0 && (
                <div>
                  <h5>Missing Required Skills</h5>
                  {renderList(missingRequiredSkills, 'tag-list tag-list-danger')}
                </div>
              )}
              {missingNiceSkills.length > 0 && (
                <div>
                  <h5>Missing Nice-to-Have Skills</h5>
                  {renderList(missingNiceSkills, 'tag-list tag-list-muted')}
                </div>
              )}
            </div>
          </section>
        )}
      </article>

      <details className="result-card technical-details">
        <summary className="technical-summary">
          <div>
            <span className="eyebrow">Diagnostics</span>
            <h4>Technical Details</h4>
          </div>
          <span className="toggle-button" aria-hidden="true">Show</span>
        </summary>
        <div className="technical-body">
          <div className="tech-grid">
            <div className="tech-item"><span>Provider</span><strong>{result.provider}</strong></div>
            <div className="tech-item"><span>File Name</span><strong>{result.file_name}</strong></div>
            <div className="tech-item"><span>Basic Heuristic Score</span><strong>{basicScores.total_score ?? 0}/100</strong></div>
            <div className="tech-item"><span>Sections Found</span><strong>{basicDetails.sections_found ?? 0}/5</strong></div>
            <div className="tech-item"><span>Raw Text Length</span><strong>{result.raw_text_length ?? 0} characters</strong></div>
            <div className="tech-item"><span>Cleaned Text Length</span><strong>{result.cleaned_text_length ?? 0} characters</strong></div>
            <div className="tech-item"><span>Analyzed Text Length</span><strong>{result.analyzed_text_length ?? 0} characters</strong></div>
            <div className="tech-item"><span>Word Count</span><strong>{resumeFeatures.word_count ?? 0}</strong></div>
            <div className="tech-item"><span>Line Count</span><strong>{resumeFeatures.line_count ?? 0}</strong></div>
            <div className="tech-item"><span>Bullet Points</span><strong>{resumeFeatures.bullet_count ?? basicDetails.bullet_points_found ?? 0}</strong></div>
            <div className="tech-item"><span>Numbers Found</span><strong>{resumeFeatures.number_count ?? 0}</strong></div>
            <div className="tech-item"><span>Has Email</span><strong>{resumeFeatures.has_email ? 'Yes' : 'No'}</strong></div>
            <div className="tech-item"><span>Has Phone</span><strong>{resumeFeatures.has_phone ? 'Yes' : 'No'}</strong></div>
            <div className="tech-item"><span>Has LinkedIn</span><strong>{resumeFeatures.has_linkedin ? 'Yes' : 'No'}</strong></div>
            <div className="tech-item"><span>Has GitHub</span><strong>{resumeFeatures.has_github ? 'Yes' : 'No'}</strong></div>
            {!isCandidate && <div className="tech-item"><span>Job Description Source</span><strong>{result.job_description_source || 'Not provided'}</strong></div>}
            {!isCandidate && <div className="tech-item"><span>Job Description Length</span><strong>{result.job_description_length ?? 0} characters</strong></div>}
          </div>
        </div>
      </details>
    </section>
  );
};

export default ResultDisplay;
