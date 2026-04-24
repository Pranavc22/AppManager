"""
Pydantic schemas for Bug RCA service
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels for bugs"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AnalysisDepth(str, Enum):
    """Analysis depth levels"""
    QUICK = "quick"
    STANDARD = "standard"
    DETAILED = "detailed"


class BugLogEntry(BaseModel):
    """Single bug log entry"""
    
    timestamp: datetime = Field(..., description="When the error occurred")
    service_name: str = Field(..., description="Service where error occurred")
    error_message: str = Field(..., description="Error message or exception")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    environment: str = Field("production", description="Environment: dev, staging, prod")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestHandler",
                "environment": "production",
                "metadata": {"region": "us-east-1"}
            }
        }


class RCAAnalysis(BaseModel):
    """Root Cause Analysis result"""
    
    root_cause: str = Field(..., description="Identified root cause")
    affected_systems: List[str] = Field(..., description="Systems affected")
    severity: SeverityLevel = Field(..., description="Severity level")
    business_impact: str = Field(..., description="Business impact")
    recommendations: List[str] = Field(..., description="Recommended actions")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence (0-1)")
    related_errors: List[str] = Field(default=[], description="Related error patterns")
    
    class Config:
        json_schema_extra = {
            "example": {
                "root_cause": "Null pointer in request validation",
                "affected_systems": ["api-gateway", "auth-service"],
                "severity": "high",
                "business_impact": "Users unable to login (15% of user base)",
                "recommendations": [
                    "Add null checks in validation",
                    "Implement input sanitization"
                ],
                "confidence_score": 0.85,
                "related_errors": ["NullPointerException"]
            }
        }


class RCARequest(BaseModel):
    """Request for RCA analysis"""
    
    logs: List[BugLogEntry] = Field(..., min_items=1, max_items=1000, description="Bug logs")
    analysis_depth: AnalysisDepth = Field(AnalysisDepth.STANDARD, description="quick, standard, or detailed")
    focus_areas: Optional[List[str]] = Field(None, description="Areas to focus on")
    
    class Config:
        json_schema_extra = {
            "example": {
                "logs": [
                    {
                        "timestamp": "2024-01-15T10:30:00Z",
                        "service_name": "api-gateway",
                        "error_message": "NullPointerException",
                        "environment": "production"
                    }
                ],
                "analysis_depth": "standard"
            }
        }


class RCAResponse(BaseModel):
    """Complete RCA response"""
    
    request_id: str = Field(..., description="Unique request ID")
    analysis: RCAAnalysis = Field(..., description="RCA analysis result")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="AI model used")
    analysis_summary: str = Field(..., description="Human-readable summary")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


# ============ Dashboard & Statistics Schemas ============

class IncidentQuestion(BaseModel):
    """Pre-populated question with current statistics"""
    
    question_id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="The question text")
    metric_name: str = Field(..., description="Name of the metric (e.g., 'total_incidents')")
    current_value: int = Field(..., description="Current value for this metric")
    description: str = Field(..., description="Detailed description of what this metric means")
    trend: str = Field("stable", description="Trend: stable, increasing, or decreasing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "question": "What is the total number of incidents?",
                "metric_name": "total_incidents",
                "current_value": 15,
                "description": "Total count of all incidents detected in the system",
                "trend": "increasing"
            }
        }


class DashboardStatistics(BaseModel):
    """Dashboard statistics with incident metrics"""
    
    total_incidents: int = Field(..., description="Total number of incidents")
    high_risk_incidents: int = Field(..., description="Number of high/critical severity incidents")
    medium_risk_incidents: int = Field(..., description="Number of medium severity incidents")
    low_risk_incidents: int = Field(..., description="Number of low severity incidents")
    service_down_causes: Dict[str, int] = Field(..., description="Breakdown of service down causes by type")
    most_common_error: str = Field(..., description="Most frequently occurring error type")
    last_incident_time: Optional[datetime] = Field(None, description="Timestamp of most recent incident")
    incident_time_window: str = Field("last_24h", description="Time window for statistics (last_24h, last_7d, last_30d)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_incidents": 42,
                "high_risk_incidents": 8,
                "medium_risk_incidents": 15,
                "low_risk_incidents": 19,
                "service_down_causes": {
                    "database_connection": 5,
                    "memory_leak": 2,
                    "timeout": 1
                },
                "most_common_error": "NullPointerException",
                "last_incident_time": "2024-01-15T10:35:00Z",
                "incident_time_window": "last_24h"
            }
        }


class DashboardResponse(BaseModel):
    """Dashboard response with pre-populated questions and statistics"""
    
    statistics: DashboardStatistics = Field(..., description="Current incident statistics")
    questions: List[IncidentQuestion] = Field(..., description="Pre-populated questions based on data")
    insights: List[str] = Field(..., description="Key insights and observations")
    suggested_investigations: List[str] = Field(..., description="Recommended areas to investigate")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "statistics": {
                    "total_incidents": 42,
                    "high_risk_incidents": 8,
                    "low_risk_incidents": 19,
                    "service_down_causes": {"database_connection": 5},
                    "most_common_error": "NullPointerException"
                },
                "questions": [
                    {
                        "question_id": "q1",
                        "question": "What is the total number of incidents?",
                        "metric_name": "total_incidents",
                        "current_value": 42
                    }
                ],
                "insights": ["High frequency of NullPointerException errors"],
                "suggested_investigations": ["Review null-safety checks in validation layer"]
            }
        }


class FullRCARequest(BaseModel):
    """Request for full RCA analysis with issue description and logs"""
    
    issue_description: str = Field(..., min_length=10, description="Detailed description of the issue")
    issue_type: str = Field(..., description="Type of issue (e.g., service_down, performance, crash)")
    affected_service: str = Field(..., description="Service that is affected")
    start_time: Optional[datetime] = Field(None, description="When the issue started")
    end_time: Optional[datetime] = Field(None, description="When the issue ended (if resolved)")
    affected_users_count: Optional[int] = Field(None, description="Estimated number of affected users")
    logs: Optional[List[BugLogEntry]] = Field(None, description="Optional provided logs (will use auto-loaded logs if not provided)")
    analysis_depth: AnalysisDepth = Field(AnalysisDepth.DETAILED, description="quick, standard, or detailed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "issue_description": "API Gateway service went down, users unable to authenticate. Multiple null pointer exceptions found in request validation",
                "issue_type": "service_down",
                "affected_service": "api-gateway",
                "start_time": "2024-01-15T10:30:00Z",
                "affected_users_count": 5000,
                "analysis_depth": "detailed"
            }
        }


class FullRCAResponse(BaseModel):
    """Complete full RCA response with detailed analysis"""
    
    request_id: str = Field(..., description="Unique request ID")
    issue_summary: str = Field(..., description="Summary of the reported issue")
    analysis: RCAAnalysis = Field(..., description="RCA analysis result")
    logs_analyzed: int = Field(..., description="Number of logs analyzed")
    timeline: List[Dict[str, Any]] = Field(..., description="Timeline of events")
    affected_services: List[str] = Field(..., description="All affected services")
    business_impact_assessment: str = Field(..., description="Detailed business impact")
    immediate_actions: List[str] = Field(..., description="Immediate actions to mitigate")
    preventive_measures: List[str] = Field(..., description="Long-term preventive measures")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="AI model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "issue_summary": "API Gateway service outage due to null pointer exceptions",
                "analysis": {
                    "root_cause": "Null pointer in request validation layer",
                    "affected_systems": ["api-gateway", "auth-service"],
                    "severity": "critical"
                },
                "logs_analyzed": 150,
                "timeline": [{"time": "2024-01-15T10:30:00Z", "event": "First error detected"}],
                "affected_services": ["api-gateway", "auth-service", "user-service"],
                "business_impact_assessment": "Complete service outage affecting 5000+ users",
                "immediate_actions": ["Roll back last deployment", "Restart API Gateway service"],
                "preventive_measures": ["Add null-safety checks", "Implement validation layer testing"],
                "confidence_score": 0.92
            }
        }


# ============ Bug Matching Schemas ============

class MatchedScenario(BaseModel):
    """Information about matched bug scenario from dataset"""
    
    scenario_id: str = Field(..., description="ID of the matched scenario (e.g., scenario_1_null_pointer)")
    scenario_name: str = Field(..., description="Human-readable name of the scenario")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Matching confidence (0-1)")
    matched_keywords: List[str] = Field(..., description="Keywords that matched the description")
    primary_error_type: str = Field(..., description="Main error type in this scenario")
    affected_services_in_scenario: List[str] = Field(..., description="Services affected in this scenario")
    error_count_in_dataset: int = Field(..., description="Number of errors in the matched dataset")
    description: str = Field(..., description="Description of what this bug scenario involves")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "scenario_1_null_pointer",
                "scenario_name": "Null Pointer Exception in Request Validation",
                "match_score": 0.95,
                "matched_keywords": ["null pointer", "request validation", "api-gateway"],
                "primary_error_type": "NullPointerException",
                "affected_services_in_scenario": ["api-gateway", "auth-service"],
                "error_count_in_dataset": 45,
                "description": "NullPointerException occurring in request validation layer"
            }
        }


class BugMatchingRequest(BaseModel):
    """Request for bug matching and RCA analysis"""
    
    bug_description: str = Field(..., min_length=10, description="User's description of the bug they encountered")
    analysis_depth: AnalysisDepth = Field(AnalysisDepth.DETAILED, description="quick, standard, or detailed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "bug_description": "Users are getting null pointer exceptions when trying to authenticate. The API gateway is crashing intermittently.",
                "analysis_depth": "detailed"
            }
        }


class BugMatchingResponse(BaseModel):
    """Response with matched bug and complete RCA analysis"""
    
    request_id: str = Field(..., description="Unique request ID")
    matched_scenario: MatchedScenario = Field(..., description="The matched bug scenario from dataset")
    issue_summary: str = Field(..., description="Summary of the matched issue")
    analysis: RCAAnalysis = Field(..., description="RCA analysis result for matched scenario")
    logs_analyzed: int = Field(..., description="Number of logs from matched scenario analyzed")
    timeline: List[Dict[str, Any]] = Field(..., description="Timeline of events from matched logs")
    affected_services: List[str] = Field(..., description="All affected services")
    business_impact_assessment: str = Field(..., description="Detailed business impact")
    immediate_actions: List[str] = Field(..., description="Immediate actions to mitigate")
    preventive_measures: List[str] = Field(..., description="Long-term preventive measures")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="AI model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "matched_scenario": {
                    "scenario_id": "scenario_1_null_pointer",
                    "scenario_name": "Null Pointer Exception in Request Validation",
                    "match_score": 0.95,
                    "matched_keywords": ["null pointer", "authentication", "api-gateway"],
                    "primary_error_type": "NullPointerException",
                    "affected_services_in_scenario": ["api-gateway", "auth-service"],
                    "error_count_in_dataset": 45,
                    "description": "NullPointerException in request validation layer"
                },
                "issue_summary": "Matched to: Null Pointer Exception in Request Validation",
                "analysis": {
                    "root_cause": "Null pointer in request validation when processing null input",
                    "affected_systems": ["api-gateway", "auth-service"],
                    "severity": "critical"
                },
                "logs_analyzed": 45,
                "timeline": [{"time": "2024-01-15T10:00:00Z", "event": "First NullPointerException"}],
                "affected_services": ["api-gateway", "auth-service"],
                "business_impact_assessment": "Authentication failures affecting multiple users",
                "immediate_actions": ["Add input validation", "Implement null checks"],
                "preventive_measures": ["Enhanced validation", "Unit test coverage"],
                "confidence_score": 0.93
            }
        }


class MatchIncidentRequest(BaseModel):
    """Request for matching a bug description to an incident in the dataset."""
    bug_description: str = Field(..., min_length=10, description="User's description of the bug or keywords.")

    class Config:
        json_schema_extra = {
            "example": {
                "bug_description": "api-gateway is getting OutOfMemoryError heap space",
            }
        }


class MatchedIncidentResponse(BaseModel):
    """Response containing the incident that best matched the description."""
    request_id: str = Field(..., description="Unique request ID for this match operation.")
    matched_scenario: Optional[MatchedScenario] = Field(None, description="The best matching bug scenario from the dataset. Null if no match found.")
    logs: List[BugLogEntry] = Field([], description="The raw logs from the matched incident scenario.")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "matched_scenario": {
                    "scenario_id": "scenario_5_memory_issues",
                    "scenario_name": "Memory Issues",
                    "match_score": 0.88,
                    "matched_keywords": ["memory", "heap", "api-gateway"],
                    "primary_error_type": "OutOfMemoryError: Java heap space",
                    "affected_services_in_scenario": ["api-gateway", "worker-service"],
                    "error_count_in_dataset": 52,
                    "description": "This scenario involves memory issues."
                },
                "logs": [
                    {
                        "timestamp": "2024-01-15T16:00:00Z",
                        "service_name": "api-gateway",
                        "error_message": "OutOfMemoryError: Java heap space",
                    }
                ]
            }
        }
