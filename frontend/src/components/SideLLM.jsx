import React, { useState } from 'react'
import "./SideLLM.css"

const SideLLM = ({ onExecute, isProcessing }) => {

  const [productDesc, setProductDesc] = useState('');

  const handleKeyDown = (e) => {
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault()
      if(productDesc.trim() !== '' && !isProcessing){
        onExecute({ description: productDesc.trim() })
      }
    }
  }

  return (
    <div className="mainSide" id='mainSIDE'>
        <header className="titleProduct">Product To Analyze</header>
        <div className="suggestion">
          <div className="histSggTxt">Click Left Anchor for Simulation History</div>
          <div className="suggestion1">Workspace 2 for final score and Insights</div>
          <div className="suggestion2">Workspace 3 for OUR Details :D</div>
        </div>
        <textarea 
          className="prDesc" 
          placeholder={isProcessing ? "Agents are computing..." : "Describe the product here... (Press Enter to execute)"}
          value={productDesc}
          onChange={(e) => setProductDesc(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isProcessing}
        ></textarea>
        <div className="designMsg">Sick Design Right? ;-;</div>
    </div>
  )
}

export default SideLLM