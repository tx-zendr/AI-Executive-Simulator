from pydantic import BaseModel, Field
from typing import List, Optional, Any, TypedDict, Dict,Annotated

class SimulationRequest(BaseModel):
    idea: str = Field(..., description="The product idea or feature request to evaluate.")
    thread_id: Optional[str] = Field(None, description="Optional unique thread ID (UUID format) to track/resume this session. Generated automatically if not supplied.")

class AgentResponse(BaseModel):
    agent_name: str = Field(..., description="The name of the agent (CEO, CFO, CTO, CMO, Customer, Competitor)")
    score: int = Field(..., description="A score from 0 to 100 representing the agent's evaluation/acceptance of the idea", ge=0, le=100)
    feedback: str = Field(..., description="A summary of the agent's opinion, reasoning, and perspective on the product idea")
    key_points: List[str] = Field(..., description="3-5 key bullet points summarizing risks, opportunities, or considerations from this agent's viewpoint")

class StakeholderScores(BaseModel):
    CEO: int = Field(..., description="CEO score from 0 to 100", ge=0, le=100)
    CFO: int = Field(..., description="CFO score from 0 to 100", ge=0, le=100)
    CTO: int = Field(..., description="CTO score from 0 to 100", ge=0, le=100)
    CMO: int = Field(..., description="CMO score from 0 to 100", ge=0, le=100)
    Customer: int = Field(..., description="Customer score from 0 to 100", ge=0, le=100)
    Competitor: int = Field(..., description="Competitor score from 0 to 100", ge=0, le=100)

class DecisionResponse(BaseModel):
    overall_decision: str = Field(..., description="The final decision recommendation. Must be one of: 'Approve', 'Revise', or 'Reject'")
    executive_feedback: str = Field(..., description="A consolidated summary of the board meeting, explaining the main dynamics and rationale for the decision")
    customer_acceptance: int = Field(..., description="Score representing simulated customer acceptance (0-100)", ge=0, le=100)
    key_risks: List[str] = Field(..., description="Top key risks identified across all executive feedback")
    recommended_improvements: List[str] = Field(..., description="Top recommended actionable improvements to address the feedback")
    confidence_score: int = Field(..., description="Confidence score in the final decision recommendation (0-100)", ge=0, le=100)
    individual_scores: StakeholderScores = Field(..., description="Raw scores from all stakeholder agents")
    Idea_Name:str =Field(...,description="Final Idea Name For the Product")

class SimulatorState(TypedDict):
    idea: str
    ceo_feedback: Optional[AgentResponse]
    cfo_feedback: Optional[AgentResponse]
    cto_feedback: Optional[AgentResponse]
    cmo_feedback: Optional[AgentResponse]
    customer_feedback: Optional[AgentResponse]
    competitor_feedback: Optional[AgentResponse]
    decision: Optional[DecisionResponse]

class SimulationResponse(BaseModel):
    thread_id: str
    decision: DecisionResponse
    agents:List[AgentResponse]

class HistoryResponse(BaseModel):
    thread_id: str
    idea: str
    decision: DecisionResponse

class ThreadListEntry(BaseModel):
    thread_id: str
    idea: str
    thread_name:Optional[str]
