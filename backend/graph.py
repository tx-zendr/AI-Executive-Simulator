import os
import psycopg
from schemas import SimulatorState
from agents import (
    call_agent, call_decision_agent,
    CEO_PROMPT, CFO_PROMPT, CTO_PROMPT, CMO_PROMPT, CUSTOMER_PROMPT, COMPETITOR_PROMPT
)
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── DB & Persistence Config ────────────────────────────────────────────────
from database import init_db
init_db()          # Ensure target DB + application tables exist

DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")
DB_NAME     = os.getenv("DB_NAME",     "AI_Decision_System")

_connection_string = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Node functions ──────────────────────────────────────────────────────────
def ceo_node(state: SimulatorState) -> dict:
    return {"ceo_feedback": call_agent("CEO", CEO_PROMPT, state["idea"])}

def cfo_node(state: SimulatorState) -> dict:
    return {"cfo_feedback": call_agent("CFO", CFO_PROMPT, state["idea"])}

def cto_node(state: SimulatorState) -> dict:
    return {"cto_feedback": call_agent("CTO", CTO_PROMPT, state["idea"])}

def cmo_node(state: SimulatorState) -> dict:
    return {"cmo_feedback": call_agent("CMO", CMO_PROMPT, state["idea"])}

def customer_node(state: SimulatorState) -> dict:
    return {"customer_feedback": call_agent("Customer", CUSTOMER_PROMPT, state["idea"])}

def competitor_node(state: SimulatorState) -> dict:
    return {"competitor_feedback": call_agent("Competitor", COMPETITOR_PROMPT, state["idea"])}

def decision_node(state: SimulatorState) -> dict:
    feedbacks = [
        state.get("ceo_feedback"),
        state.get("cfo_feedback"),
        state.get("cto_feedback"),
        state.get("cmo_feedback"),
        state.get("customer_feedback"),
        state.get("competitor_feedback"),
    ]
    feedbacks = [f for f in feedbacks if f is not None]
    return {"decision": call_decision_agent(state["idea"], feedbacks)}

# ── Graph Definition ────────────────────────────────────────────────────────
workflow = StateGraph(SimulatorState)

workflow.add_node("ceo",        ceo_node)
workflow.add_node("cfo",        cfo_node)
workflow.add_node("cto",        cto_node)
workflow.add_node("cmo",        cmo_node)
workflow.add_node("customer",   customer_node)
workflow.add_node("competitor", competitor_node)
workflow.add_node("decision",   decision_node)

# Parallel fan-out from START
workflow.add_edge(START, "ceo")
workflow.add_edge(START, "cfo")
workflow.add_edge(START, "cto")
workflow.add_edge(START, "cmo")
workflow.add_edge(START, "customer")
workflow.add_edge(START, "competitor")

# Converge all agents onto decision node
workflow.add_edge("ceo",        "decision")
workflow.add_edge("cfo",        "decision")
workflow.add_edge("cto",        "decision")
workflow.add_edge("cmo",        "decision")
workflow.add_edge("customer",   "decision")
workflow.add_edge("competitor", "decision")

workflow.add_edge("decision", END)

# ── Checkpointer (PostgresSaver) ───────────────────────────────────────────
# PostgresSaver requires a raw psycopg2 connection, not a context manager.
# We open a dedicated, long-lived connection for the checkpointer.
_pg_conn = psycopg.connect(_connection_string, autocommit=True)

checkpointer = PostgresSaver(_pg_conn)
# Create the internal langgraph checkpoint tables if they don't exist yet
checkpointer.setup()

# ── Compile ────────────────────────────────────────────────────────────────
app = workflow.compile(checkpointer=checkpointer)
print("[Graph] Compiled successfully with PostgresSaver checkpointer.")
