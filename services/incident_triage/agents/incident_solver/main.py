import json

from services.incident_triage.agents.incident_solver.prompt import INCIDENT_ANALYSIS_SYSTEM
from utils.llm import get_llm_client


class IncidentAnalysisAgent:
    def __init__(self):
        self.client = get_llm_client()

    def analyze(self, context: dict) -> dict:      
        incident = context["incident"]
        similar = context["similar_incidents"]

        # Keep context compact
        clean_context = {
            "current_incident": {
                "short_description": incident["short_description"],
                "description": incident["description"]
            },
            "similar_incidents": [
                {
                    "short_description": inc["short_description"],
                    "description": inc["description"],
                    "resolution": inc.get("resolution", "")
                }
                for inc in similar
            ]
        }

        user_prompt = f"""
        Analyze the following incident and provide structured output.

        Context:
        {json.dumps(clean_context, indent=2)}

        Return JSON with:
        {{
        "summary": "...",
        "root_cause": "...",
        "recommendation": "...",
        "confidence": "High | Medium | Low",
        "estimated_effort": "Few hours | 1 day | Multiple days"
        }}
        """
        try:
            response = self.client.chat(
                system=INCIDENT_ANALYSIS_SYSTEM,
                user=user_prompt
            )
            print(f"LLM response: {response}")
            # Safe JSON parsing
            return json.loads(response)
        
        except Exception as e:
            print(f"AI failed due to: {e}")
            return {
                "summary": "The incident could not be summarized.",
                "root_cause": "The RCA could not be made.",
                "recommendation": "The AI system could not come up with a recommendation",
                "confidence": "Low",
                "estimated_effort": "Unknown"
            }