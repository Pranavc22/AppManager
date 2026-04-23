"""
Integration guide for RCA Agent with other services
"""

from services.bug_rca.graph import RCAWorkflow
from services.bug_rca.schemas.base_schema import RCARequest, RCAResponse


class RCAServiceIntegration:
    """
    Integration wrapper for using RCA service with other agents
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize RCA service for integration
        
        Args:
            llm_client: Optional LLM client for Gemini/OpenRouter integration
        """
        # The WorkflowGraph is removed for a more direct and dynamic approach.
        # We now use RCAWorkflow directly, injecting the LLM client.
        self.workflow = RCAWorkflow(llm_client=llm_client)
    
    def analyze_logs(
        self,
        logs: list,
        analysis_depth: str = "standard",
        focus_areas: list = None
    ) -> dict:
        """
        Analyze bug logs - main integration point
        
        Args:
            logs: List of bug log dictionaries
            analysis_depth: "quick", "standard", or "detailed"
            focus_areas: Areas to focus analysis
            
        Returns:
            Dictionary with RCA analysis results
        """
        
        # Create request
        request = RCARequest(
            logs=logs,
            analysis_depth=analysis_depth,
            focus_areas=focus_areas
        )
        
        # Execute analysis using the single, more dynamic workflow
        response = self.workflow.execute(request)
        
        # Return as dictionary for easy integration
        return response.model_dump()
    
    def get_analysis_summary(self, response: dict) -> str:
        """Extract summary from analysis response"""
        return response.get("analysis_summary", "Analysis complete")
    
    def get_root_cause(self, response: dict) -> str:
        """Extract root cause from analysis response"""
        analysis = response.get("analysis", {})
        return analysis.get("root_cause", "Unknown")
    
    def get_recommendations(self, response: dict) -> list:
        """Extract recommendations from analysis response"""
        analysis = response.get("analysis", {})
        return analysis.get("recommendations", [])
    
    def get_affected_systems(self, response: dict) -> list:
        """Extract affected systems from analysis response"""
        analysis = response.get("analysis", {})
        return analysis.get("affected_systems", [])


# ============ Usage Examples for Other Agents ============

def integrate_with_incident_triage():
    """
    Example: How IncidentTriage agent can use RCA service
    """
    
    # Initialize RCA service
    rca = RCAServiceIntegration()
    
    # Example incident logs
    logs = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "service_name": "api-gateway",
            "error_message": "Connection timeout",
            "environment": "production"
        }
    ]
    
    # Get RCA analysis
    analysis = rca.analyze_logs(logs, analysis_depth="standard")
    
    # Use results in incident triage workflow
    root_cause = rca.get_root_cause(analysis)
    severity = analysis["analysis"]["severity"]
    recommendations = rca.get_recommendations(analysis)
    affected_systems = rca.get_affected_systems(analysis)
    
    # Return enriched incident data
    incident_context = {
        "root_cause": root_cause,
        "severity": severity,
        "recommendations": recommendations,
        "affected_systems": affected_systems,
        "analysis_confidence": analysis["analysis"]["confidence_score"]
    }
    
    return incident_context


def integrate_with_user_access():
    """
    Example: How UserAccess agent can use RCA service
    """
    
    rca = RCAServiceIntegration()
    
    # Authentication-related errors
    auth_logs = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "service_name": "auth-service",
            "error_message": "Invalid token validation",
            "environment": "production",
            "user_id": "user_123"
        }
    ]
    
    # Focus on authentication issues
    analysis = rca.analyze_logs(
        auth_logs,
        analysis_depth="detailed",
        focus_areas=["authentication", "token_validation"]
    )
    
    # Extract relevant data for access management
    return {
        "authentication_issue": rca.get_root_cause(analysis),
        "affected_users": rca.get_affected_systems(analysis),
        "recommendations": rca.get_recommendations(analysis)
    }


def integrate_with_custom_agent():
    """
    Example: Custom agent using RCA service
    """
    
    class CustomAgent:
        def __init__(self):
            self.rca = RCAServiceIntegration()
        
        def process_error(self, error_logs):
            """Process error logs using RCA service"""
            
            analysis = self.rca.analyze_logs(
                error_logs,
                analysis_depth="standard"
            )
            
            # Use RCA results in custom logic
            confidence = analysis["analysis"]["confidence_score"]
            severity = analysis["analysis"]["severity"]
            
            if confidence > 0.8 and severity in ["critical", "high"]:
                # Take action based on high-confidence, high-severity analysis
                return self._take_action(analysis)
            else:
                # Lower confidence - escalate for review
                return {"status": "escalated", "analysis": analysis}
        
        def _take_action(self, analysis):
            """Take action based on RCA analysis"""
            return {
                "status": "action_taken",
                "actions": analysis["analysis"]["recommendations"]
            }
    
    # Example usage
    agent = CustomAgent()
    result = agent.process_error([{
        "timestamp": "2024-01-15T10:30:00Z",
        "service_name": "critical-service",
        "error_message": "Critical failure",
        "environment": "production"
    }])
    
    return result


if __name__ == "__main__":
    # Example integrations
    print("=== Incident Triage Integration ===")
    incident_context = integrate_with_incident_triage()
    print(incident_context)
    
    print("\n=== User Access Integration ===")
    access_context = integrate_with_user_access()
    print(access_context)
    
    print("\n=== Custom Agent Integration ===")
    custom_result = integrate_with_custom_agent()
    print(custom_result)
