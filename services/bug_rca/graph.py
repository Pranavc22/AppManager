"""
Agent workflow graph for RCA service
Defines the state machine and dynamic workflow for bug RCA analysis
"""

from typing import Dict, Any, Optional
from enum import Enum

from services.bug_rca.schemas.base_schema import RCARequest, RCAResponse
from services.bug_rca.agents.agent1.main import RCAAgent


class WorkflowState(str, Enum):
    """Workflow states"""
    IDLE = "idle"
    PROCESSING = "processing"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"


class RCAWorkflow:
    """
    RCA Workflow
    Manages the state machine and workflow for RCA analysis.
    This is the main entry point for an analysis request.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize workflow
        
        Args:
            llm_client: Optional LLM client for RCA Agent
        """
        self.agent = RCAAgent(llm_client)
        self.state = WorkflowState.IDLE
        self.current_context = {}
    
    def execute(self, request: RCARequest) -> RCAResponse:
        """
        Execute the RCA analysis workflow
        
        Args:
            request: RCARequest object
            
        Returns:
            RCAResponse object
        """
        
        try:
            # 1. Validate input
            self.state = WorkflowState.VALIDATING
            self._validate_request(request)
            
            # 2. Process and enrich input for the LLM
            self.state = WorkflowState.PROCESSING
            enriched_request = self._process_input(request)
            
            # 3. Run analysis using the agent
            self.state = WorkflowState.ANALYZING
            response = self.agent.analyze(enriched_request)
            
            # 4. Completed
            self.state = WorkflowState.COMPLETED
            return response
            
        except Exception as e:
            self.state = WorkflowState.ERROR
            self.current_context["error"] = str(e)
            raise
    
    def _process_input(self, request: RCARequest) -> RCARequest:
        """
        Process and enrich the request before sending to the LLM agent.
        This is where dynamic adjustments can be made based on input.
        
        For example, we could add log frequency, or even use a smaller LLM
        to classify the error type and add that as a focus area.
        """
        # Dynamically add focus_areas based on log content
        if request.logs:
            # Check for common error patterns in log messages
            log_messages = [log.error_message for log in request.logs]
            
            # Initialize focus_areas if not set
            if not request.focus_areas:
                request.focus_areas = []
            
            # Add dynamic focus areas based on error message patterns
            error_text = " ".join(log_messages).lower()
            
            if "database" in error_text and "database" not in request.focus_areas:
                request.focus_areas.append("database")
            
            if "timeout" in error_text and "timeout" not in request.focus_areas:
                request.focus_areas.append("timeout")
                
            if "memory" in error_text and "memory" not in request.focus_areas:
                request.focus_areas.append("memory")
                
            if "auth" in error_text and "authentication" not in request.focus_areas:
                request.focus_areas.append("authentication")
                
        return request
    
    def _validate_request(self, request: RCARequest) -> bool:
        """Validate RCA request"""
        
        if not request.logs or len(request.logs) == 0:
            raise ValueError("At least one log entry is required")
        
        if len(request.logs) > 1000:
            raise ValueError("Maximum 1000 log entries allowed")
        
        if request.analysis_depth not in ["quick", "standard", "detailed"]:
            raise ValueError("analysis_depth must be: quick, standard, or detailed")
        
        return True
    
    def get_state(self) -> WorkflowState:
        """Get current workflow state"""
        return self.state
    
    def reset(self) -> None:
        """Reset workflow state"""
        self.state = WorkflowState.IDLE
        self.current_context = {}
