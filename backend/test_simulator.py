import os
import sys
from dotenv import load_dotenv

# Ensure local imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from graph import app as graph_app

def main():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment!")
        print("Please configure .env before running this script.")
        sys.exit(1)

    test_idea = "A subscription-based smart food bowl that automatically detects pet food levels and orders refills via Amazon API when low."
    print("--- Running AI Executive Simulator Board Meeting ---")
    print(f"Product Idea: '{test_idea}'\n")

    try:
        # Run graph workflow
        result = graph_app.invoke({"idea": test_idea})

        print("--- Node Execution Complete ---")
        
        # Display individual board member reports
        print("\n=== BOARD MEMBER FEEDBACKS ===")
        for key in ["ceo_feedback", "cfo_feedback", "cto_feedback", "cmo_feedback", "customer_feedback", "competitor_feedback"]:
            fb = result.get(key)
            if fb:
                print(f"\n[{fb.agent_name} - Score: {fb.score}/100]")
                print(f"Feedback: {fb.feedback}")
                print("Key Points:")
                for kp in fb.key_points:
                    print(f"  - {kp}")
            else:
                print(f"\n[{key} missing feedback!]")

        # Display compiled board decision
        print("\n=== FINAL BOARD DECISION REPORT ===")
        decision = result.get("decision")
        if decision:
            print(f"Overall Decision: {decision.overall_decision}")
            print(f"Confidence Score: {decision.confidence_score}/100")
            print(f"Customer Acceptance Score: {decision.customer_acceptance}/100")
            print(f"Executive Board Feedback:\n{decision.executive_feedback}")
            print("\nKey Risks:")
            for risk in decision.key_risks:
                print(f"  - {risk}")
            print("\nRecommended Improvements:")
            for imp in decision.recommended_improvements:
                print(f"  - {imp}")
            print(f"\nIndividual Scores: {decision.individual_scores}")
        else:
            print("ERROR: Decision response was not set.")

        print("\nSimulation successfully completed!")
    except Exception as e:
        print(f"Error during simulation execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
