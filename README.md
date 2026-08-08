# 🤖 AI Executive Simulator

### Your AI-Powered Virtual Executive Board for Stress-Testing Business Ideas

**AI Executive Simulator** is a multi-agent AI decision-making platform that evaluates business and product ideas from multiple stakeholder perspectives before you invest time, money, and resources into building them.

Instead of asking a single AI whether an idea is good, the simulator creates a **virtual executive board** consisting of six specialized AI agents:

> **CEO • CFO • CTO • CMO • Customer • Competitor**

Each agent independently analyzes the idea from its own perspective. **LangGraph** orchestrates the agents and combines their evaluations through a final **Decision Agent**, producing a consolidated recommendation:

**✅ Approve | 🔄 Revise | ❌ Reject**

The system is powered by **Google Gemini 2.5 Flash**, uses **PostgreSQL** for persistent data and LangGraph checkpoints, and exposes a **FastAPI backend** that can be connected to a React/Next.js frontend.

---

## ✨ What Makes It Different?

Most AI idea evaluators provide a single opinion.

**AI Executive Simulator creates an entire AI boardroom.**

A business idea is challenged from:

| AI Agent          | Perspective                                                 |
| ----------------- | ----------------------------------------------------------- |
| 👔 **CEO**        | Strategy, vision, growth, scalability & long-term viability |
| 💰 **CFO**        | Cost, revenue, pricing, ROI & financial risk                |
| 💻 **CTO**        | Technical feasibility, architecture, security & scalability |
| 📈 **CMO**        | Market positioning, customer acquisition & branding         |
| 👤 **Customer**   | User needs, pain points, usefulness & willingness to pay    |
| ⚔️ **Competitor** | Competitive threats, alternatives & defensibility           |

The final Decision Agent synthesizes all six perspectives into a single executive report.

---

# 🧠 System Architecture

```text
                         ┌─────────────────────┐
                         │     Frontend UI      │
                         │ React / Next.js      │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST API
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI         │
                         │     Backend         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      LangGraph      │
                         │  Agent Orchestrator │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
         ┌─────────┐           ┌─────────┐           ┌─────────┐
         │   CEO   │           │   CFO   │           │   CTO   │
         └────┬────┘           └────┬────┘           └────┬────┘
              │                     │                     │
              ├─────────────────────┼─────────────────────┤
              │                     │                     │
              ▼                     ▼                     ▼
         ┌─────────┐           ┌──────────┐          ┌────────────┐
         │   CMO   │           │ Customer │          │ Competitor  │
         └────┬────┘           └────┬─────┘          └─────┬──────┘
              │                     │                      │
              └─────────────────────┼──────────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  Decision Agent     │
                         │  Board Synthesis    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Final Evaluation   │
                         │                     │
                         │ Approve / Revise /  │
                         │ Reject              │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    PostgreSQL       │
                         │ Persistent Storage  │
                         └─────────────────────┘
```

The LangGraph workflow fans the idea out to all six stakeholder nodes and then converges their outputs into the final Decision Agent.

---

# 🚀 Core Features

### 🏢 Multi-Agent Executive Board

Six specialized AI agents independently evaluate every submitted idea.

Each agent returns:

* Score from **0–100**
* Detailed feedback
* Key risks
* Opportunities
* Important considerations

The response schema explicitly defines these fields for every stakeholder.

---

### 🧩 LangGraph Orchestration

The system uses **LangGraph StateGraph** to coordinate the entire simulation.

The workflow:

1. Receives the business idea
2. Sends it to six stakeholder agents
3. Collects their evaluations
4. Sends all evaluations to the Decision Agent
5. Generates the final board recommendation
6. Persists the results

## The stakeholder nodes are connected in a parallel fan-out architecture before converging on the decision node.

### 🧠 Google Gemini 2.5 Flash

The simulator uses **Google Gemini 2.5 Flash** as the underlying reasoning model.

Responses are generated using structured JSON schemas so that every agent returns predictable, machine-readable results.
The system also includes:

* API rate limiting
* Automatic retry handling
* Exponential backoff
* Structured response validation

## This helps the multi-agent workflow operate reliably under API rate limits.

# 🏆 Final Board Decision

After all agents finish their evaluations, the **Decision Agent** analyzes the complete board feedback.

It produces:

* **Overall Decision**

  * ✅ Approve
  * 🔄 Revise
  * ❌ Reject
* **Customer Acceptance Score**
* **Confidence Score**
* **Executive Board Feedback**
* **Key Risks**
* **Recommended Improvements**
* **Individual Stakeholder Scores**

These outputs are defined in the `DecisionResponse` schema.

---

# 🗄️ PostgreSQL Persistence

The application uses **PostgreSQL** to store simulation data and historical evaluations.

The database contains:

### `User_Data`

Stores:

* Thread ID
* Business idea
* User-related simulation data

### `Agents`

Stores:

* Agent name
* Score
* Feedback
* Key points

### `Decision`

Stores:

* Overall decision
* Confidence score
* Customer acceptance
* Executive feedback
* Key risks
* Recommended improvements

The database schema and relationships are defined in the project SQL configuration.
The backend also automatically initializes the required database/tables when the application starts.

---

# 🔄 Persistent Conversations & Simulation History

Each simulation receives a unique `thread_id`.

This allows the system to:

* Track individual simulations
* Resume/retrieve previous sessions
* Store historical board evaluations
* Retrieve complete decision reports

LangGraph uses **PostgresSaver** as its checkpoint system for persistent workflow state.

---

# 🌐 FastAPI Backend

The backend is built using **FastAPI** and provides REST endpoints for the frontend.

### API Endpoints

#### `GET /`

Checks whether the API is running.

#### `POST /simulate`

Submit a business/product idea for evaluation.

Example:

```json
{
  "idea": "A smart subscription service that automatically manages household supplies."
}
```

The endpoint executes the LangGraph workflow and returns the stakeholder evaluations and final decision.

---

#### `GET /history/{thread_id}`

Retrieves the complete evaluation history for a specific simulation.

```text
GET /history/{thread_id}
```

---

#### `GET /threads`

Returns previously created simulations and their corresponding ideas.

```text
GET /threads
```

---

# 🎨 Frontend Integration

The backend is designed to communicate with a **React / Next.js frontend** through REST APIs.

CORS is enabled so the frontend can communicate with the FastAPI backend.

### Frontend Flow

```text
User enters idea
       ↓
Frontend
       ↓
POST /simulate
       ↓
FastAPI
       ↓
LangGraph
       ↓
6 AI Agents
       ↓
Decision Agent
       ↓
PostgreSQL
       ↓
FastAPI Response
       ↓
Frontend Dashboard
       ↓
Results & Insights
```

The frontend can visualize:

* Individual agent scores
* Executive feedback
* Customer acceptance
* Confidence score
* Key risks
* Recommended improvements
* Final Approve/Revise/Reject decision

---

# 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**
* **Pydantic**

### AI / Agentic AI

* **Google Gemini 2.5 Flash**
* **LangGraph**
* Multi-Agent Architecture
* Structured AI Outputs

### Database

* **PostgreSQL**
* **Psycopg / Psycopg2**
* LangGraph PostgreSQL Checkpointing

### Frontend

* **React / Next.js**
* REST API integration

The backend dependencies currently include FastAPI, Uvicorn, LangGraph, Google GenAI, Pydantic, python-dotenv, and PostgreSQL support.

---

# 📁 Project Structure

```text
AI-Executive-Simulator/
│
├── agents.py
├── database.py
├── database_query.txt
├── graph.py
├── main.py
├── schemas.py
├── test.py
├── test_simulator.py
├── requirements.txt
├── .gitignore
│
└── frontend/
    └── ...
```

### Important Backend Files

| File                 | Purpose                                         |
| -------------------- | ----------------------------------------------- |
| `agents.py`          | Defines AI executive personas and Gemini calls  |
| `graph.py`           | Defines the LangGraph multi-agent workflow      |
| `database.py`        | PostgreSQL connection, storage & history        |
| `schemas.py`         | Pydantic models and LangGraph state definitions |
| `main.py`            | FastAPI REST API                                |
| `database_query.txt` | PostgreSQL database schema                      |
| `test.py`            | API testing                                     |
| `test_simulator.py`  | Simulator workflow testing                      |
| `requirements.txt`   | Python dependencies                             |

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/tx-zendr/AI-Executive-Simulator.git

cd AI-Executive-Simulator
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the backend root directory.

```env
GEMINI_API_KEY=your_gemini_api_key

DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=AI_Decision_System
```

The application reads the Gemini API key and PostgreSQL configuration from environment variables.
**Never commit your `.env` file or API keys to GitHub.**

---

# 🐘 PostgreSQL Setup

Make sure PostgreSQL is installed and running.

The application can initialize the target database and required tables automatically during startup.

Alternatively, the SQL schema is available in:

```text
database_query.txt
```

---

# ▶️ Running the Backend

Start the FastAPI server with:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 🧪 Testing

You can test the simulator directly using:

```bash
python test_simulator.py
```

Or test the API using:

```bash
python test.py
```

The project also contains a sample simulation workflow that submits an idea and prints all six board-member evaluations followed by the final decision report.

---

# 💡 Example

### Input

```text
I want to build a smart subscription service that automatically
orders household products when they are running low.
```

### AI Executive Board

```text
CEO
→ Strategic viability: 82/100

CFO
→ Financial feasibility: 76/100

CTO
→ Technical feasibility: 88/100

CMO
→ Market potential: 79/100

Customer
→ Customer acceptance: 91/100

Competitor
→ Competitive advantage: 68/100
```

### Final Decision

```text
Decision: REVISE

Confidence: 84/100

Customer Acceptance: 91/100

Key Risks:
- Customer acquisition cost
- Competitor replication
- API dependency

Recommended Improvements:
- Strengthen differentiation
- Improve pricing strategy
- Build a stronger retention mechanism
```

*Example output shown for illustration; actual scores depend on the submitted idea and model response.*

---

# 🎯 Use Cases

AI Executive Simulator can be used for:

* 🚀 Startup idea validation
* 💡 Product idea evaluation
* 🏆 Hackathon projects
* 📊 Business strategy analysis
* 💰 Financial feasibility analysis
* 💻 Technical feasibility assessment
* 📈 Marketing strategy evaluation
* 👤 Customer-centric product validation
* ⚔️ Competitive analysis
* 🧠 AI-assisted strategic decision making

---

# 🔮 Future Improvements

Potential future extensions include:

* 🌐 Real-time market research
* 📊 Live competitor data
* 💰 Financial forecasting
* 📈 Market-size estimation
* 🔎 Web-powered research agents
* 🧠 Long-term organizational memory
* 🤝 More specialized executive agents
* 📄 Automated business reports
* 📊 Advanced analytics dashboard
* 🔐 Authentication and multi-user workspaces
* ☁️ Cloud deployment
* 📱 Mobile interface

---

# ⚠️ Disclaimer

AI Executive Simulator provides **AI-generated strategic analysis**, not professional financial, legal, investment, or business advice.

The recommendations should be treated as decision-support information and independently validated before making real-world business decisions.

---

# 👨‍💻 Built With

**Python • FastAPI • LangGraph • Google Gemini • PostgreSQL • React/Next.js**

> **Don't just ask AI if your idea is good. Put your idea in front of an entire AI executive board.**

---

## ⭐ If you find this project useful

Give the repository a ⭐ and feel free to contribute, open issues, or suggest new executive agents and simulation capabilities.
