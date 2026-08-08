import os
import time
import threading
from typing import List
from google import genai
from google.genai import types
from dotenv import load_dotenv
from schemas import AgentResponse, DecisionResponse, StakeholderScores
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_message

# Load environment variables
load_dotenv()

# Initialize the Gemini Client
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Recommended model
MODEL_NAME = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Rate Limiter: 5 RPM → 1 call every 13 seconds (safe margin)
# A threading.Lock ensures all parallel Langgraph nodes queue up here,
# so we never fire more than 1 Gemini call per RATE_INTERVAL_SECONDS.
# ---------------------------------------------------------------------------
RATE_INTERVAL_SECONDS = 13          # seconds between consecutive API calls
_rate_lock = threading.Lock()
_last_call_time: float = 0.0        # timestamp of the most recent API call

def _wait_for_rate_limit():
    """
    Acquires the global rate-limit lock and sleeps until at least
    RATE_INTERVAL_SECONDS have passed since the last Gemini API call.
    This serialises every call, even when Langgraph nodes run in parallel threads.
    """
    global _last_call_time
    with _rate_lock:
        now = time.time()
        elapsed = now - _last_call_time
        wait = RATE_INTERVAL_SECONDS - elapsed
        if wait > 0:
            print(f"[Rate Limiter] Waiting {wait:.1f}s before next API call …")
            time.sleep(wait)
        _last_call_time = time.time()

# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------
CEO_PROMPT = """You are the Chief Executive Officer (CEO) of a multi-billion dollar corporation.
Your priority is long-term vision, strategic alignment, high-level business feasibility, growth, and brand value.
Evaluate the proposed product idea or feature request from a strategic standpoint.
Determine if it aligns with modern corporate strategy, brand expansion, and long-term viability.
Be constructive but critical. Provide a realistic score and clear bullet points."""

CFO_PROMPT = """You are the Chief Financial Officer (CFO) of the company.
Your priority is cost, monetization, pricing models, revenue potential, profit margins, ROI, financial feasibility, and fiscal risk.
Evaluate the proposed product idea. Analyze how it will make money, what the cost drivers might be (infrastructure, operations, etc.), and what the potential profit margin looks like.
Provide a realistic score and clear bullet points outlining financial opportunities and risks."""

CTO_PROMPT = """You are the Chief Technology Officer (CTO) of the company.
Your priority is technical feasibility, systems architecture, scalability, security, development effort/time, maintenance, and technical debt.
Evaluate the proposed product idea. Analyze what technology stack is required, the complexity of implementation, scalability concerns, integration risks, and security issues.
Provide a realistic score and clear bullet points outlining technical advantages and concerns."""

CMO_PROMPT = """You are the Chief Marketing Officer (CMO) of the company.
Your priority is customer acquisition, branding, market positioning, target audience, pricing psychology, and launch strategy.
Evaluate the proposed product idea. Analyze if it has a clear value proposition, who the target audience is, what acquisition channels are available, and how marketable the idea is.
Provide a realistic score and clear bullet points outlining marketing opportunities and risks."""

CUSTOMER_PROMPT = """You are a Simulated Target Customer.
You represent the end-user's perspective. Your concerns are solving real pain points, ease of use, utility, value for money, and delight.
Evaluate the proposed product idea. Do you actually want this product? Would you pay for it? Does it solve a real problem for you, or is it a solution in search of a problem?
Provide a realistic score and clear bullet points outlining customer concerns and desires."""

COMPETITOR_PROMPT = """You are a Competitor Analysis Agent.
Your role is to think like a rival company in the same space.
Evaluate the proposed product idea. Analyze how easily rivals can clone it, what market alternatives exist, what barriers to entry the company can create, and what counter-strategies competitors might launch.
Provide a realistic score (higher = strong, defensible advantage; lower = easy to replicate) and clear bullet points outlining competitive threats and defensibility."""

DECISION_PROMPT = """You are the Board Chairman / Decision Agent.
You are presented with a product idea and the detailed evaluations of six key stakeholders: CEO, CFO, CTO, CMO, Customer, and Competitor.
Your role is to synthesize these viewpoints, balance conflicting feedback, and make a final recommendation:
- Approve: feedback is highly positive and risks are manageable.
- Revise: promising idea but needs specific changes.
- Reject: fatal flaws, poor financials, or no competitive advantage.

Generate a comprehensive consolidated board report, calculate a combined customer acceptance score, list top key risks, recommended improvements, a final confidence score, and record all individual stakeholder scores."""

# ---------------------------------------------------------------------------
# Gemini caller with tenacity retry (catches 429 and server errors)
# ---------------------------------------------------------------------------
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=15, max=60),
    reraise=True
)
def _generate_with_retry(contents: str, config: types.GenerateContentConfig):
    """Calls Gemini API with automatic exponential-backoff retry on rate-limit errors."""
    _wait_for_rate_limit()
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config
    )

# ---------------------------------------------------------------------------
# Public helpers used by graph.py
# ---------------------------------------------------------------------------
def call_agent(agent_name: str, system_prompt: str, idea: str) -> AgentResponse:
    """Evaluates the product idea through a single board-member persona."""
    print(f"[Agent] Calling {agent_name} …")
    try:
        response = _generate_with_retry(
            contents=f"Evaluate this product idea: {idea}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=AgentResponse,
                temperature=0.2,
            )
        )
        if response.parsed:
            print(f"[Agent] {agent_name} responded with score {response.parsed.score}.")
            return response.parsed
        raise ValueError("No parsed response received from Gemini")
    except Exception as e:
        print(f"[Agent] {agent_name} failed: {e}")
        return AgentResponse(
            agent_name=agent_name,
            score=50,
            feedback=f"Failed to evaluate idea: {str(e)[:200]}",
            key_points=["API error occurred", f"Details: {str(e)[:150]}"]
        )


def call_decision_agent(idea: str, feedbacks: List[AgentResponse]) -> DecisionResponse:
    """Synthesises all board feedback into a final consolidated decision report."""
    print("[Decision Agent] Synthesising board feedback …")

    feedback_text = "\n\n".join([
        f"Stakeholder: {f.agent_name}\nScore: {f.score}/100\n"
        f"Feedback: {f.feedback}\nKey Points: {', '.join(f.key_points)}"
        for f in feedbacks if f is not None
    ])

    prompt = (
        f"Product Idea: {idea}\n\n"
        f"Board Member Feedback:\n{feedback_text}\n\n"
        "Based on the above feedback from all stakeholders, please make a final decision, "
        "summarize the board meeting, and outline key risks and recommended improvements."
    )

    try:
        response = _generate_with_retry(
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=DECISION_PROMPT,
                response_mime_type="application/json",
                response_schema=DecisionResponse,
                temperature=0.2,
            )
        )
        if response.parsed:
            print(f"[Decision Agent] Final decision: {response.parsed.overall_decision}")
            return response.parsed
        raise ValueError("No parsed decision response received from Gemini")
    except Exception as e:
        print(f"[Decision Agent] Failed: {e}")
        scores = StakeholderScores(
            CEO=next((f.score for f in feedbacks if f.agent_name == "CEO"), 50),
            CFO=next((f.score for f in feedbacks if f.agent_name == "CFO"), 50),
            CTO=next((f.score for f in feedbacks if f.agent_name == "CTO"), 50),
            CMO=next((f.score for f in feedbacks if f.agent_name == "CMO"), 50),
            Customer=next((f.score for f in feedbacks if f.agent_name == "Customer"), 50),
            Competitor=next((f.score for f in feedbacks if f.agent_name == "Competitor"), 50),
        )
        return DecisionResponse(
            overall_decision="Revise",
            executive_feedback=f"Decision agent error: {str(e)[:200]}",
            customer_acceptance=50,
            key_risks=["API error during consolidation"],
            recommended_improvements=["Retry with a valid API connection"],
            confidence_score=0,
            individual_scores=scores
        )
