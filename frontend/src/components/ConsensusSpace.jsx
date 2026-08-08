import React from 'react'
import "./ConsensusSpace.css"

const ConsensusSpace = ({ decision }) => {
  if (!decision) {
    return (
      <div className="consensus-empty">
        <h1>Awaiting Board Decision</h1>
      </div>
    );
  }
  const verdictColor = decision.overall_decision === 'Approve' ? 'var(--accent-secondary)' : 
                       decision.overall_decision === 'Revise' ? '#fbbf24' : 'var(--accent-danger)';

  return (
    <div className="consensus-main">
      <div className="consensus-header" style={{ borderColor: verdictColor }}>
        
        <div className="verdict-block">
          <h2>BOARD VERDICT</h2>
          <h1 style={{ color: verdictColor, textShadow: `0 0 15px ${verdictColor}` }}>
            {decision.overall_decision.toUpperCase()}
          </h1>
        </div>
        <div className="center-static-block">
          <div className="static-line"><span>//</span> SIMULATION_PHASE_COMPLETE</div>
          <div className="static-line"><span>//</span> NEURAL_CONSENSUS_REACHED</div>
          <div className="static-line"><span>//</span> ALL_AGENTS_SYNCHRONIZED</div>
        </div>

        <div className="score-block">
          <h2>CONFIDENCE</h2>
          <h1>{decision.confidence_score}%</h1>
        </div>
        
      </div>
      
      <div className="consensus-summary">
        <h3>Executive Feedback</h3>
        <p>{decision.executive_feedback}</p>
      </div>
      
      <div className="consensus-details">
        <div className="details-col risks">
          <h3 style={{ color: 'var(--accent-danger)' }}>Critical Risks</h3>
          <ul>
            {decision.key_risks.map((risk, i) => (
              <li key={i}>{risk}</li>
            ))}
          </ul>
        </div>
        
        <div className="details-col improvements">
          <h3 style={{ color: 'var(--accent-secondary)' }}>Recommended Improvements</h3>
          <ul>
            {decision.recommended_improvements.map((improvement, i) => (
              <li key={i}>{improvement}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ConsensusSpace