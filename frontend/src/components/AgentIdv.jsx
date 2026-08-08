import React from 'react'
import "./AgentIdv.css"

const AgentIdv = ({ title, desc, iconUrl, apiResult, isProcessing }) => {
  
  let displayText = desc; 
  if (isProcessing) {
    displayText = "Analyzing market parameters...";
  } else if (apiResult && apiResult.feedback) {
    displayText = apiResult.feedback; 
  }

  return (
    <div className="mainAgIdv" style={{ opacity: isProcessing ? 0.6 : 1 }}>
        <div className="placeholderAg">
          <div className="topBar">
            <div className="leftSide">
              <div className="iconSpace" style={{ backgroundImage: `url(${iconUrl})` }}></div>
            </div>
            <div className="rightSide">
              <div className="nameSpace">{title}</div>
              
              {apiResult && !isProcessing && (
                <div className="scoreBadge">{apiResult.score}%</div>
              )}
            </div>
          </div>
          
          <div className="personalityText">
             {displayText}
          </div>
        </div>
    </div>
  )
}

export default AgentIdv