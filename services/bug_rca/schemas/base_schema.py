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
    analysis_depth: str = Field("standard", description="quick, standard, or detailed")
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
