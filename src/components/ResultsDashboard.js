import React from 'react';

function ResultsDashboard({ data, onReset }) {
  const { match_analysis, learning_roadmap } = data;

  return (
    <div className="results-dashboard">
      <button onClick={onReset} className="back-button">← Analyze Another</button>
      
      <div className="summary-card">
        <h2>{match_analysis.match_percentage}% Match</h2>
        <p>{match_analysis.summary}</p>
      </div>

      <div className="skills-grid">
        <div className="skills-list matching-skills">
          <h3>✅ Matching Skills</h3>
          <ul>
            {match_analysis.details.matching_skills.map(skill => (
              <li key={skill.skill}>{skill.skill}</li>
            ))}
          </ul>
        </div>
        <div className="skills-list missing-skills">
          <h3>❌ Missing Skills</h3>
          <ul>
            {match_analysis.details.missing_skills.map(skill => (
              <li key={skill.skill}>{skill.skill}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="roadmap">
        <h3>Your Personalized Learning Roadmap</h3>
        {learning_roadmap.length > 0 ? (
          learning_roadmap.map(step => (
            <div key={step.step} className="roadmap-step">
              <h4>Step {step.step}: Learn {step.skill}</h4>
              <div className="step-details">
                <span><strong>Difficulty:</strong> {step.difficulty}</span>
                <span><strong>Est. Time:</strong> {step.estimated_weeks} weeks</span>
              </div>
              <div className="resource-list">
                <h5>🎓 Recommended Resources:</h5>
                <ul>
                  {step.resources.map((resource, index) => (
                    <li key={index}>
                      <a href={resource.url} target="_blank" rel="noopener noreferrer">
                        {resource.title} ({resource.type})
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))
        ) : (
          <p>Congratulations! No critical skills are missing for this role.</p>
        )}
      </div>
    </div>
  );
}

export default ResultsDashboard;