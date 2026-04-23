"""
FastAPI router for Bug RCA Service
Provides REST API endpoints for RCA analysis
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List

from services.bug_rca.schemas.base_schema import (
    RCARequest, RCAResponse, BugLogEntry
)
from services.bug_rca.graph import RCAWorkflow

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router and workflow
router = APIRouter()
workflow_graph = RCAWorkflow()

def compress_logs(logs: List[BugLogEntry]) -> List[BugLogEntry]:
    """Compress log entries by grouping identical errors to reduce token usage."""
    if not logs:
        return logs
        
    grouped = {}
    for log in logs:
        # Create a unique signature for this error type
        sig = f"{log.service_name}::{log.error_message}"
        if sig not in grouped:
            grouped[sig] = log.model_copy() if hasattr(log, "model_copy") else log.copy()
            if grouped[sig].metadata is None:
                grouped[sig].metadata = {}
            grouped[sig].metadata["occurrences"] = 1
            grouped[sig].metadata["first_seen"] = str(log.timestamp)
            grouped[sig].metadata["last_seen"] = str(log.timestamp)
        else:
            grouped[sig].metadata["occurrences"] += 1
            grouped[sig].metadata["last_seen"] = str(log.timestamp)
            
    return list(grouped.values())


# ============ Health Check Endpoints ============

@router.get("/", tags=["Health"])
def read_root():
    """Service root endpoint"""
    return {
        "service": "bug_rca",
        "message": "Bug Report/Logs Summary + RCA Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze"
        }
    }


@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bug_rca",
        "version": "1.0.0"
    }


# ============ RCA Analysis Endpoints ============

@router.post(
    "/analyze",
    response_model=RCAResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"],
    summary="Perform Root Cause Analysis on bug logs",
    responses={
        200: {"description": "Successful analysis"},
        400: {"description": "Invalid request"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
def analyze_logs(request: RCARequest) -> RCAResponse:
    """
    Analyze bug logs and generate Root Cause Analysis
    
    **Request Parameters:**
    - `logs`: List of bug log entries (required, 1-50 entries)
    - `analysis_depth`: Level of analysis - "quick", "standard", or "detailed" (default: "standard")
    - `focus_areas`: Specific areas to focus on (optional)
    
    **Response:**
    Returns complete RCA analysis with root cause identification, affected systems, 
    severity assessment, business impact, and recommendations.
    
    **Example Request:**
    ```json
    {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestHandler",
                "environment": "production"
            }
        ],
        "analysis_depth": "standard",
        "focus_areas": ["authentication", "validation"]
    }
    ```
    
    **Example Response:**
    ```json
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "analysis": {
            "root_cause": "Null pointer in request validation",
            "affected_systems": ["api-gateway", "auth-service"],
            "severity": "high",
            "business_impact": "Users unable to authenticate affecting 15% of user base",
            "recommendations": [
                "Add null-safety checks in validation layer",
                "Implement input sanitization",
                "Add monitoring for this error pattern"
            ],
            "confidence_score": 0.85,
            "related_errors": []
        },
        "processing_time_ms": 2350.5,
        "model_used": "openrouter-llm",
        "analysis_summary": "Analyzed 1 bug logs. Root Cause: Null pointer in request validation. Severity: HIGH...",
        "timestamp": "2024-01-15T10:35:00Z"
    }
    ```
    """
    
    try:
        logger.info(f"Received RCA analysis request with {len(request.logs)} logs")
        
        # Validate request
        if not request.logs or len(request.logs) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one log entry is required"
            )
        
        if len(request.logs) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 1000 log entries allowed per request"
            )
            
        # Compress logs to save tokens
        original_count = len(request.logs)
        request.logs = compress_logs(request.logs)
        logger.info(f"Compressed {original_count} logs down to {len(request.logs)} unique signatures")
        
        # Execute analysis
        response = workflow_graph.execute(request)
        
        logger.info(f"RCA analysis completed. Request ID: {response.request_id}")
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in RCA analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during RCA analysis"
        )


@router.post(
    "/quick-analyze",
    response_model=RCAResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"],
    summary="Quick RCA analysis (performance optimized)"
)
def quick_analyze(request: RCARequest) -> RCAResponse:
    """
    Quick analysis endpoint (optimized for speed)
    
    Similar to /analyze but forces "quick" analysis depth for faster response
    """
    
    try:
        # Force quick analysis depth
        request.analysis_depth = "quick"
        
        logger.info(f"Received quick RCA analysis request with {len(request.logs)} logs")
        request.logs = compress_logs(request.logs)
        response = workflow_graph.execute(request)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Quick analysis failed"
        )


@router.post(
    "/detailed-analyze",
    response_model=RCAResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"],
    summary="Detailed RCA analysis (comprehensive)"
)
def detailed_analyze(request: RCARequest) -> RCAResponse:
    """
    Detailed analysis endpoint (comprehensive analysis)
    
    Similar to /analyze but forces "detailed" analysis depth for thorough results
    """
    
    try:
        # Force detailed analysis depth
        request.analysis_depth = "detailed"
        
        logger.info(f"Received detailed RCA analysis request with {len(request.logs)} logs")
        request.logs = compress_logs(request.logs)
        response = workflow_graph.execute(request)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in detailed analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detailed analysis failed"
        )


# ============ Batch Analysis Endpoints ============

@router.post(
    "/batch-analyze",
    status_code=status.HTTP_200_OK,
    tags=["Batch Operations"],
    summary="Analyze multiple log batches"
)
def batch_analyze(requests: List[RCARequest]) -> List[RCAResponse]:
    """
    Analyze multiple RCA requests in batch
    
    **Parameters:**
    - `requests`: Array of RCARequest objects
    
    **Returns:**
    Array of RCAResponse objects in the same order as requests
    """
    
    try:
        logger.info(f"Received batch analysis with {len(requests)} requests")
        
        responses = []
        for req in requests:
            try:
                req.logs = compress_logs(req.logs)
                response = workflow_graph.execute(req)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error in batch item: {str(e)}")
                # Optionally skip failed items or return error response
                continue
        
        logger.info(f"Batch analysis completed with {len(responses)} successful items")
        return responses
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch analysis failed"
        )


# ============ Information Endpoints ============

import os
import glob
from pathlib import Path

@router.get(
    "/datasets",
    tags=["Information"],
    summary="Get list of available log datasets"
)
def get_datasets():
    """Get all available JSON log files in the data directory"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    log_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    datasets = []
    for file in log_files:
        datasets.append({
            "id": os.path.basename(file),
            "name": os.path.basename(file).replace(".json", "").replace("_", " ").title(),
            "path": file
        })
    
    return {"datasets": datasets}

import json

@router.get(
    "/dataset/{dataset_id}",
    tags=["Information"],
    summary="Get specific dataset content by ID"
)
def get_dataset(dataset_id: str):
    """Get the JSON content of a specific dataset log file"""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    file_path = os.path.join(data_dir, dataset_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
        
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Error reading dataset {dataset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read dataset file"
        )

@router.get(
    "/info",
    tags=["Information"],
    summary="Get service information"
)
def get_info():
    """Get service metadata and capabilities"""
    
    return {
        "service": "bug_rca",
        "description": "Root Cause Analysis for bug logs",
        "version": "1.0.0",
        "capabilities": {
            "analysis_depths": ["quick", "standard", "detailed"],
            "max_logs_per_request": 50,
            "features": [
                "Error pattern extraction",
                "System dependency mapping",
                "Severity assessment",
                "Business impact analysis",
                "Actionable recommendations"
            ]
        },
        "endpoints": {
            "analyze": "POST /analyze",
            "quick_analyze": "POST /quick-analyze",
            "detailed_analyze": "POST /detailed-analyze",
            "batch_analyze": "POST /batch-analyze"
        }
    }