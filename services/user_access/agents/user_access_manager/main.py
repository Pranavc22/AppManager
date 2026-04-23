from utils.llm import get_llm_client
from services.user_access.agents.user_access_manager.prompt import *

class SummaryAgent:
    def __init__(self):
        self.client = get_llm_client()

    def generate_summary(self, context: dict) -> str:
        system_prompt = SYSTEM

        user_prompt = f"""
        Generate a summary for the following request:

        {context}
        """         

        response = self.client.chat(
            system=system_prompt,
            user=user_prompt,
            max_tokens=200
        )

        return response.strip()