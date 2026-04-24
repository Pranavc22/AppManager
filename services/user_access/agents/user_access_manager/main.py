import json

from utils.llm import get_llm_client
from services.user_access.agents.user_access_manager.prompt import *
from services.user_access.utils.query import get_user_id_from_request, assign_roles, update_request_status, insert_access_decision

class SummaryAgent:
    def __init__(self):
        self.client = get_llm_client()

    def generate_summary(self, context: dict) -> str:
        clean_context = {
            "user_name": context["user_name"],
            "action": context["requested_action"],
            "resource": context["resource_name"],
            "study": context["scope_id"]
        }

        system_prompt = SUMMARY_SYSTEM
        user_prompt = f"""
        Generate a summary for the following request:
        {clean_context}
        """         

        response = self.client.chat(
            system=system_prompt,
            user=user_prompt,
            max_tokens=200
        )

        return response.strip()

class DecisionAgent:
    def __init__(self):
        self.client = get_llm_client()

    def generate_decision(self, payload: dict) -> dict:
        system_prompt = DECISION_SYSTEM
        user_prompt = f"""
        Analyze the following access request:

        {json.dumps(payload, indent=2)}
        """

        response = self.client.chat(
            system=system_prompt,
            user=user_prompt,
            temperature=0.0
        )

        try:
            return json.loads(response)
        except Exception as e:
            # fallback
            print(f"Exception in loading response: {e}")
            return {
                "risk": "MEDIUM",
                "impact": "Unable to determine impact",
                "decision": "REVIEW",
                "confidence": "LOW",
                "reason": "System ran into an error, would require human intervention."
            }
        
class UpsertAgent:
        
    def upsert_decision(request_id: str, payload):
        decision = payload.decision.upper()

        user_id = get_user_id_from_request(request_id)

        if not user_id:
            raise ValueError("Invalid request_id")

        if decision == "APPROVE":
            # assign roles
            assign_roles(user_id, [r.dict() for r in payload.roles_to_assign])

            update_request_status(request_id, "APPROVED")

        elif decision == "REJECT":
            update_request_status(request_id, "REJECTED")

        else:
            raise ValueError("Invalid decision")

        # insert decision record
        insert_access_decision(
            request_id=request_id,
            approver_id=payload.approver_id,
            decision=decision,
            comments=payload.comments
        )