import { useState } from 'react'
import './App.css'
import { fetchSimulation, fetchThreadHistory } from './utils/api'
import Waybar from './components/Waybar'
import SideLLM from './components/SideLLM'
import AgentSpace from './components/AgentSpace'
import ConsensusSpace from './components/ConsensusSpace'
import About from './components/About'
import HistorySidebar from './components/HistorySidebar'

function App(){
  const [activeSpace, setActiveSpace] = useState(1)
  const [isProcessing, setIsProcessing] = useState(false)
  const [agentResults, setAgentResults] = useState([]) 
  const [consensus, setConsensus] = useState(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const handleWorkspaceSwitch = (newId, direction) => {
    setActiveSpace(newId);
  }
  const handleExecutePrompt = async (productData) => {
    setIsProcessing(true);
    const data = await fetchSimulation(productData);
    if (data) {
      setAgentResults(data.agents);
      setConsensus(data.decision);
      setActiveSpace(2); 
    }
    setIsProcessing(false);
  }
  const handleLoadHistory = async (thread_id) => {
    setIsProcessing(true);
    setIsSidebarOpen(false); 
    setActiveSpace(1); 

    const data = await fetchThreadHistory(thread_id);
    
    if (data) {
      setAgentResults(data.agents);
      setConsensus(data.decision);
    }
    
    setIsProcessing(false);
  }

  return (
    <>
      <div className="os-root">
        <nav>
          <Waybar 
            activeSpace={activeSpace} 
            onWorkspaceSwitch={handleWorkspaceSwitch} 
            isProcessing={isProcessing} 
          />
        </nav>
        <button 
           className="history-anchor-btn" 
           onClick={() => setIsSidebarOpen(true)}
        >
        </button>

        <HistorySidebar 
            isOpen={isSidebarOpen} 
            onClose={() => setIsSidebarOpen(false)} 
            onLoadHistory={handleLoadHistory}
        />

        <div className="workspace-viewport">
          <div 
            className="workspace-slider"
            style={{ transform: `translateX(-${(activeSpace - 1) * 100}vw)` }}
          >
            <div className="workspace-screen">
              <SideLLM onExecute={handleExecutePrompt} isProcessing={isProcessing} />
              <AgentSpace data={agentResults} isProcessing={isProcessing} />
            </div>
            <div className="workspace-screen">
              <ConsensusSpace decision={consensus} />
            </div>
            <div className="workspace-screen">
              <div style={{color: "white", fontSize: "2rem", padding: "20px"}} id='usWSP'>
                <About />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default App