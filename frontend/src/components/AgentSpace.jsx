import React from 'react'
import "./AgentSpace.css"
import AgentIdv from './AgentIdv'

const defaultAgents = [
  { id: 1, rawName: "CEO", title: 'C E O', desc: 'Focuses on overall strategy, vision, and market positioning.', icon: '/ceo.png' },
  { id: 2, rawName: "CTO", title: 'C T O', desc: 'Evaluates technical feasibility, architecture, and innovation.', icon: '/cto.png' },
  { id: 3, rawName: "CFO", title: 'C F O', desc: 'Analyzes costs, ROI, and financial viability.', icon: '/cfo.png' },
  { id: 4, rawName: "CMO", title: 'C M O', desc: 'Strategizes marketing, branding, and user acquisition.', icon: '/cmo.png' },
  { id: 5, rawName: "Customer", title: 'CUSTOMER', desc: 'Represents the end-user needs, pain points, and UX.', icon: '/customer.png' },
  { id: 6, rawName: "Competitor", title: 'COMPETITOR', desc: 'Identifies weaknesses, market threats, and alternative solutions.', icon: '/competitor.png' }
];

const AgentSpace = ({ data, isProcessing }) => {
  return (
    <div className="mainAgSp" id='mainAGSP'>
        {defaultAgents.map((defaultAgent) => {
          const apiResult = data ? data.find(
            (a) => a.agent_name.toLowerCase() === defaultAgent.rawName.toLowerCase()
          ) : null;

          return (
            <AgentIdv 
              key={defaultAgent.id}
              title={defaultAgent.title}
              desc={defaultAgent.desc}       
              iconUrl={defaultAgent.icon}    
              apiResult={apiResult}         
              isProcessing={isProcessing}
            />
          )
        })}
    </div>
  )
}

export default AgentSpace