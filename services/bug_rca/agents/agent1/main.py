"""
Main RCA Agent - orchestrates bug analysis using LLM
"""

import json
import logging
import time
import uuid
from typing import Optional, Dict, Any, List

from services.bug_rca.schemas.base_schema import (
    RCARequest, RCAResponse, RCAAnalysis, SeverityLevel, BugLogEntry
)
from services.bug_rca.agents.agent1 import tools, prompt

logger = logging.getLogger(__name__)


class RCAAgent:
    """
    Root Cause Analysis Agent
    Analyzes bug logs and generates RCA recommendations
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize RCA Agent
        
        Args:
            llm_client: Optional LLM client (if None, will use mock/demo mode)
        """
        self.llm_client = llm_client
        self.model_name = "openrouter-llm"
        self.name = "RCA-Agent"
    
    def analyze(self, request: RCARequest) -> RCAResponse:
        """
        Main analysis method
        
        Args:
            request: RCARequest with logs and parameters
            
        Returns:
            RCAResponse with analysis results
        """
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"[{request_id}] Starting RCA analysis with {len(request.logs)} logs")
        
        try:
            # Step 1: Extract patterns using tools
            logs_data = [log.model_dump() if isinstance(log, BugLogEntry) else log for log in request.logs]
            
            error_patterns = tools.extract_error_patterns(logs_data)
            timeline = tools.analyze_error_timeline(logs_data)
            affected_systems = tools.identify_affected_systems(logs_data)
            stack_traces = tools.extract_stack_trace_patterns(logs_data)
            
            logger.debug(f"[{request_id}] Extracted error patterns: {error_patterns}")
            
            # Step 2: Prepare analysis context
            system_prompt = prompt.get_system_prompt(request.analysis_depth)
            analysis_instruction = prompt.get_analysis_instruction(
                len(logs_data),
                request.focus_areas,
                error_patterns
            )
            formatted_logs = prompt.format_logs_for_analysis(logs_data)
            
            full_prompt = f"""{system_prompt}

LOGS TO ANALYZE:
{formatted_logs}

{analysis_instruction}"""
            
            # Step 3: Call LLM or use analysis tools
            if self.llm_client:
                try:
                    response_text = self.llm_client.generate(full_prompt)
                    analysis_data = self._extract_json_response(response_text)
                    logger.debug(f"[{request_id}] LLM response received")
                except Exception as e:
                    logger.warning(f"[{request_id}] LLM failed, using fallback analysis: {e}")
                    analysis_data = self._fallback_analysis(
                        logs_data, error_patterns, affected_systems, stack_traces
                    )
            else:
                # Fallback analysis when no LLM is available
                analysis_data = self._fallback_analysis(
                    logs_data, error_patterns, affected_systems, stack_traces
                )
            
            # Step 4: Validate and construct response
            analysis = self._construct_rca_analysis(analysis_data)
            processing_time_ms = (time.time() - start_time) * 1000
            
            summary = tools.format_analysis_summary(
                len(logs_data),
                analysis.root_cause,
                analysis.severity,
                analysis.confidence_score
            )
            
            response = RCAResponse(
                request_id=request_id,
                analysis=analysis,
                processing_time_ms=processing_time_ms,
                model_used=self.model_name,
                analysis_summary=summary
            )
            
            logger.info(f"[{request_id}] RCA analysis completed in {processing_time_ms:.0f}ms")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] Error in RCA analysis: {str(e)}", exc_info=True)
            raise
    
    def _extract_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        
        # Try to find JSON in code block
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text
        
        # Parse JSON
        data = json.loads(json_str)
        return data
    
    def _fallback_analysis(
        self,
        logs: List[Dict[str, Any]],
        error_patterns: Dict[str, Any],
        affected_systems: List[str],
        stack_traces: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback analysis when LLM is not available
        Uses rule-based analysis
        """
        
        # Determine root cause
        most_common_error = error_patterns.get("most_common_error", "Unknown error")
        most_freq_value = error_patterns.get("error_frequency_percent", 0.0)
        
        root_cause = f"{most_common_error}"
        if "null" in most_common_error.lower():
            root_cause += " - Missing or invalid data validation"
        elif "timeout" in most_common_error.lower():
            root_cause += " - Service dependency or resource constraint"
        elif "connection" in most_common_error.lower():
            root_cause += " - Network or infrastructure issue"
        
        # Determine severity
        severity = tools.calculate_severity(most_freq_value, len(logs), False)
        
        # Business impact
        business_impact = tools.assess_business_impact(
            affected_systems, severity, most_common_error
        )
        
        # Recommendations
        recommendations = tools.generate_recommendations(
            root_cause, affected_systems, error_patterns.get("error_types", {})
        )
        
        # Related errors
        error_types = error_patterns.get("error_types", {})
        related_errors = [err for err in error_types.keys() if err != most_common_error][:3]
        
        return {
            "root_cause": root_cause,
            "affected_systems": affected_systems,
            "severity": severity,
            "business_impact": business_impact,
            "recommendations": recommendations,
            "confidence_score": 0.65,  # Lower confidence for rule-based fallback
            "related_errors": related_errors
        }
    
    def _construct_rca_analysis(self, analysis_data: Dict[str, Any]) -> RCAAnalysis:
        """Construct and validate RCAAnalysis object"""
        
        # Validate required fields
        required_fields = ["root_cause", "affected_systems", "severity", "business_impact", "recommendations", "confidence_score"]
        
        for field in required_fields:
            if field not in analysis_data:
                if field == "affected_systems":
                    analysis_data[field] = ["unknown"]
                elif field == "recommendations":
                    analysis_data[field] = ["Monitor this error pattern"]
                elif field == "related_errors":
                    analysis_data[field] = []
                else:
                    analysis_data[field] = "Unable to determine"
        
        # Ensure severity is valid
        try:
            severity = SeverityLevel(analysis_data.get("severity", "medium"))
        except ValueError:
            severity = SeverityLevel.MEDIUM
        
        # Ensure confidence is in range
        confidence = max(0.0, min(1.0, float(analysis_data.get("confidence_score", 0.5))))
        
        return RCAAnalysis(
            root_cause=str(analysis_data.get("root_cause", "Unknown")),
            affected_systems=list(analysis_data.get("affected_systems", [])),
            severity=severity,
            business_impact=str(analysis_data.get("business_impact", "Unable to determine")),
            recommendations=list(analysis_data.get("recommendations", [])),
            confidence_score=confidence,
            related_errors=list(analysis_data.get("related_errors", []))
        )
