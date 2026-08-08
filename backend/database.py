import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Any
from schemas import AgentResponse, DecisionResponse, StakeholderScores

def get_db_connection():
    """Returns a connection to the PostgreSQL database using environment variables."""
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "AI_Decision_System")
    
    return psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

def init_db():
    """Initializes the database and tables on application startup."""
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "AI_Decision_System")
    
    # 1. Connect to postgres default DB, create target DB if it doesn't exist
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database="postgres"
    )
    conn.autocommit = True
    db_existed = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            if cur.fetchone():
                db_existed = True
            else:
                # Database name cannot be parameterised in DDL — safe because it's from .env
                cur.execute(f'CREATE DATABASE "{database}"')
    finally:
        conn.close()

    # 2. Connect to the newly created / existing target database
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    try:
        with conn.cursor() as cur:
            # Create User_Data table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS User_Data (
                UID SERIAL PRIMARY KEY,
                Thread_id UUID UNIQUE NOT NULL,
                Images TEXT,
                Ideas TEXT
            );
            """)

            # Create Agents table using a composite primary key
            cur.execute("""
            CREATE TABLE IF NOT EXISTS Agents (
                Thread_id UUID,
                Agent_name VARCHAR(255) NOT NULL,
                Score DECIMAL(5,2),
                Feedback TEXT,
                Key_Points TEXT,
                PRIMARY KEY (Thread_id, Agent_name),
                CONSTRAINT fk_agent_thread
                    FOREIGN KEY (Thread_id)
                    REFERENCES User_Data(Thread_id)
                    ON DELETE CASCADE
            );
            """)

            # Create Decision table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS Decision (
                Thread_id UUID PRIMARY KEY,
                Confidence_Score DECIMAL(5,2),
                Customer_Acceptance VARCHAR(255),
                Recommend_Improvement TEXT,
                Executive_Feedback TEXT,
                Key_risks TEXT,
                Overall_Decision TEXT,
                CONSTRAINT fk_decision_thread
                    FOREIGN KEY (Thread_id)
                    REFERENCES User_Data(Thread_id)
                    ON DELETE CASCADE
            );
            """)
            #4. Thread Name 
            # Create Thread_Name table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Thread_Name (
                Thread_id UUID PRIMARY KEY,
                Thread_name VARCHAR(255) NOT NULL,
                CONSTRAINT fk_thread_name
                FOREIGN KEY (Thread_id)
                REFERENCES User_Data(Thread_id)
                ON DELETE CASCADE
                );
                """)
            
            # Index for fast thread-name lookup
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_thread_name_thread
                ON Thread_Name(Thread_id);
            """)

            # Create Indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_thread ON User_Data(Thread_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_agents_thread ON Agents(Thread_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_decision_thread ON Decision(Thread_id);")
            
        conn.commit()
    finally:
        conn.close()

def save_simulation_results(thread_id: str, idea: str, agents_feedback: List[AgentResponse], decision: DecisionResponse):
    """Saves the simulator outputs into User_Data, Agents, and Decision tables."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Upsert into User_Data
            cur.execute(
                """
                INSERT INTO User_Data (Thread_id, Ideas)
                VALUES (%s, %s)
                ON CONFLICT (Thread_id) DO UPDATE SET Ideas = EXCLUDED.Ideas;
                """,
                (thread_id, idea)
            )

            # 2. Upsert into Agents feedback table
            for agent in agents_feedback:
                if agent:
                    cur.execute(
                        """
                        INSERT INTO Agents (Thread_id, Agent_name, Score, Feedback, Key_Points)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (Thread_id, Agent_name) DO UPDATE SET
                            Score = EXCLUDED.Score,
                            Feedback = EXCLUDED.Feedback,
                            Key_Points = EXCLUDED.Key_Points;
                        """,
                        (
                            thread_id,
                            agent.agent_name,
                            agent.score,
                            agent.feedback,
                            " | ".join(agent.key_points)
                        )
                    )

            # 3. Upsert into Decision report table
            cur.execute(
                """
                INSERT INTO Decision (
                    Thread_id, Confidence_Score, Customer_Acceptance, 
                    Recommend_Improvement, Executive_Feedback, Key_risks, Overall_Decision
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (Thread_id) DO UPDATE SET
                    Confidence_Score = EXCLUDED.Confidence_Score,
                    Customer_Acceptance = EXCLUDED.Customer_Acceptance,
                    Recommend_Improvement = EXCLUDED.Recommend_Improvement,
                    Executive_Feedback = EXCLUDED.Executive_Feedback,
                    Key_risks = EXCLUDED.Key_risks,
                    Overall_Decision = EXCLUDED.Overall_Decision;
                """,
                (
                    thread_id,
                    decision.confidence_score,
                    str(decision.customer_acceptance),
                    " | ".join(decision.recommended_improvements),
                    decision.executive_feedback,
                    " | ".join(decision.key_risks),
                    decision.overall_decision
                )
            )
            # 4. Upsert into Thread_Name
            thread_name=decision.Idea_Name
            cur.execute(
                """
                INSERT INTO Thread_Name (Thread_id, Thread_name)
                VALUES (%s, %s)
                ON CONFLICT (Thread_id) DO UPDATE SET
                    Thread_name = EXCLUDED.Thread_name;
                """,
                (thread_id, thread_name)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_simulation_history(thread_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full simulation feedback and decision data for a given thread_id."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Fetch User_Data & Decision
            cur.execute(
                """
                SELECT u.Ideas as idea, d.* 
                FROM User_Data u
                LEFT JOIN Decision d ON u.Thread_id = d.Thread_id
                WHERE u.Thread_id = %s
                """,
                (thread_id,)
            )
            decision_row = cur.fetchone()
            if not decision_row:
                return None
            
            # Fetch individual agents feedback
            cur.execute(
                """
                SELECT Agent_name, Score, Feedback, Key_Points 
                FROM Agents
                WHERE Thread_id = %s
                """,
                (thread_id,)
            )
            agent_rows = cur.fetchall()
            
            # Format raw agent results into schemas
            individual_scores = {}
            agents_feedback = []
            for row in agent_rows:
                agent_name = row["agent_name"]
                score = int(row["score"])
                individual_scores[agent_name] = score
                agents_feedback.append(AgentResponse(
                    agent_name=agent_name,
                    score=score,
                    feedback=row["feedback"],
                    key_points=[kp.strip() for kp in row["key_points"].split("|")] if row["key_points"] else []
                ))

            # Pad scores if any are missing
            for role in ["CEO", "CFO", "CTO", "CMO", "Customer", "Competitor"]:
                if role not in individual_scores:
                    individual_scores[role] = 50

            scores_model = StakeholderScores(
                CEO=individual_scores.get("CEO", 50),
                CFO=individual_scores.get("CFO", 50),
                CTO=individual_scores.get("CTO", 50),
                CMO=individual_scores.get("CMO", 50),
                Customer=individual_scores.get("Customer", 50),
                Competitor=individual_scores.get("Competitor", 50)
            )
           
            decision_data = DecisionResponse(
                overall_decision=decision_row.get("overall_decision") or "Revise",
                executive_feedback=decision_row.get("executive_feedback") or "",
                customer_acceptance=int(decision_row.get("customer_acceptance") or 50),
                key_risks=[kr.strip() for kr in decision_row["key_risks"].split("|")] if decision_row.get("key_risks") else [],
                recommended_improvements=[ri.strip() for kr in [decision_row.get("recommend_improvement")] for ri in kr.split("|") if kr] if decision_row.get("recommend_improvement") else [],
                confidence_score=int(decision_row.get("confidence_score") or 50),
                individual_scores=scores_model
            )

            return {
                "thread_id": thread_id,
                "idea": decision_row["idea"],
                "decision": decision_data,
                "agents": agents_feedback
            }
    finally:
        conn.close()

def get_all_threads() -> List[Dict[str, Any]]:
    """Returns a list of all thread IDs and their corresponding ideas."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    u.Thread_id AS thread_id,
                    t.Thread_name AS thread_name,
                    u.Ideas AS idea
                FROM User_Data u
                LEFT JOIN Thread_Name t
                    ON u.Thread_id = t.Thread_id
                ORDER BY u.UID DESC
            """)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
