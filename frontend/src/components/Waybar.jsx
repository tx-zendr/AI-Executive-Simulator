import React, { useState } from 'react'
import './Waybar.css'
const Waybar = ({ activeSpace, onWorkspaceSwitch, isProcessing }) => {
  const [status, setStatus] = useState(2) 
  const statusList = ["Offline", "Server Offline", "Online"]

  const handleSwitch = (newId) => {
    if (newId === activeSpace) return;
    const direction = newId > activeSpace ? 'left' : 'right'
    
    if (onWorkspaceSwitch) {
        onWorkspaceSwitch(newId, direction)
    }
  }

  const handleStatusCycle = () => {
    setStatus((prev) => (prev + 1) % statusList.length)
  }

  const getOrbColor = () => {
    switch(status) {
      case 0: return 'var(--accent-danger)'; 
      case 1: return '#fbbf24';              
      case 2: return 'var(--accent-secondary)'; 
      default: return 'var(--accent-secondary)';
    }
  }

  return (
    <div className='mainBar'>
        <div className="modulesLeft">
            <div className="appName">AI Executive Simulator</div>
            <div className="workspaceId">
                <div 
                    className={activeSpace === 1 ? "active-ws" : ""} 
                    onClick={() => handleSwitch(1)}
                >1</div>
                <div 
                    className={activeSpace === 2 ? "active-ws" : ""} 
                    onClick={() => handleSwitch(2)}
                >2</div>
                <div 
                    className={activeSpace === 3 ? "active-ws" : ""} 
                    onClick={() => handleSwitch(3)}
                >3</div>
            </div>
        </div>
        
        <div className="modulesCentre">
            <div className="currStatus">
              {isProcessing ? "Running Simulations..." : "Awaiting Input"}
            </div>
        </div>
        
        <div className="modulesRight">
            <div className="sessionStatus" onClick={handleStatusCycle} style={{ cursor: "pointer" }}>
                <div className="orb" style={{ backgroundColor: getOrbColor() }}></div>
                <div className="statusText">{statusList[status]}</div>
            </div>
        </div>
    </div>
  )
}

export default Waybar