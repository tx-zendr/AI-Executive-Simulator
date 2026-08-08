import os
import uuid
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from schemas import (
    SimulationRequest, 
    SimulationResponse, 
    HistoryResponse, 
    ThreadListEntry
)
from graph import app as graph_app
from database import (
    init_db, 
    save_simulation_results, 
    get_simulation_history, 
    get_all_threads
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify that the API Key exists
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set. API calls will fail.")

app = FastAPI(
    title="AI Executive Simulator API",
    description="Backend for simulated executive board meetings evaluating product ideas, built with FastAPI, Langgraph, and Gemini.",
    version="1.0.0"
)

# Enable CORS for Next.js / React UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Initializes the PostgreSQL database and tables on server startup."""
    try:
        init_db()
        print("Database successfully initialized and tables verified!")
    except Exception as e:
        print(f"Error during database initialization: {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Executive Simulator API is running.",
        "endpoints": {
            "POST /simulate": "Simulate a board meeting for a product idea.",
            "GET /threads": "List all active thread ids and product ideas.",
            "GET /history/{thread_id}": "Retrieve full history and board results for a specific thread id."
        }
    }

@app.post("/simulate", response_model=SimulationResponse)
def simulate_idea(request: SimulationRequest):
    try:
        # Determine the thread_id
        if request.thread_id:
            thread_id = request.thread_id
        else:
            thread_id = str(uuid.uuid4())

        # Config with thread_id for Langgraph Postgres persistence
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # Run the compiled Langgraph workflow
        result = graph_app.invoke(
            {"idea": request.idea},
            config=config
        )
        
        # Check if decision was successfully set
        decision = result.get("decision")
        if not decision:
            raise HTTPException(
                status_code=500,
                detail="The simulation ran, but the Decision Agent failed to produce a final recommendation."
            )

        # Collect stakeholder agent feedbacks
        feedbacks = [
            result.get("ceo_feedback"),
            result.get("cfo_feedback"),
            result.get("cto_feedback"),
            result.get("cmo_feedback"),
            result.get("customer_feedback"),
            result.get("competitor_feedback")
        ]
        feedbacks = [f for f in feedbacks if f is not None]

        # Save outputs into database tables
        save_simulation_results(
            thread_id=thread_id,
            idea=request.idea,
            agents_feedback=feedbacks,
            decision=decision
        )

        return SimulationResponse(
            thread_id=thread_id,
            decision=decision,
            agents=feedbacks
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during board simulation: {str(e)}"
        )

@app.get("/history/{thread_id}", response_model=HistoryResponse)
def get_history(thread_id: str):
    """Retrieves the full historical board meeting evaluations and results for a given thread_id."""
    try:
        history = get_simulation_history(thread_id)
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No simulation history found for thread_id: {thread_id}"
            )
        return HistoryResponse(
            thread_id=history["thread_id"],
            idea=history["idea"],
            decision=history["decision"],
            agents=history["agents"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve simulation history: {str(e)}"
        )

@app.get("/threads", response_model=List[ThreadListEntry])
def list_threads():
    """Lists all past simulations along with their corresponding thread IDs and ideas."""
    try:
        threads = get_all_threads()
        return [
            ThreadListEntry(
                thread_id=t["thread_id"],
                idea=t["idea"],
                thread_name=t["thread_name"]
            )
            for t in threads
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve thread list: {str(e)}"
        )


# Inside main.py
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)