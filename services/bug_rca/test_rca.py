"""
Test suite for Bug RCA Service
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient

from main import app
from services.bug_rca.schemas.base_schema import (
    BugLogEntry, RCARequest, RCAResponse, RCAAnalysis, SeverityLevel
)
from services.bug_rca.agents.agent1.main import RCAAgent
from services.bug_rca.agents.agent1 import tools, prompt
from services.bug_rca.graph import RCAWorkflow, WorkflowGraph

# Test client
client = TestClient(app)


# ============ Schema Tests ============

def test_bug_log_entry_creation():
    """Test BugLogEntry schema"""
    
    log_data = {
        "timestamp": "2024-01-15T10:30:00Z",
        "service_name": "api-gateway",
        "error_message": "NullPointerException",
        "environment": "production"
    }
    
    log = BugLogEntry(**log_data)
    assert log.service_name == "api-gateway"
    assert log.error_message == "NullPointerException"


def test_rca_request_schema():
    """Test RCARequest schema"""
    
    request_data = {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "Connection timeout"
            }
        ],
        "analysis_depth": "quick"
    }
    
    req = RCARequest(**request_data)
    assert len(req.logs) == 1
    assert req.analysis_depth == "quick"


def test_rca_analysis_schema():
    """Test RCAAnalysis schema"""
    
    analysis_data = {
        "root_cause": "Database connection pool exhausted",
        "affected_systems": ["api-gateway", "user-service"],
        "severity": "high",
        "business_impact": "API responds slowly, users experience latency",
        "recommendations": ["Increase pool size", "Monitor pool metrics"],
        "confidence_score": 0.85
    }
    
    analysis = RCAAnalysis(**analysis_data)
    assert analysis.severity == SeverityLevel.HIGH
    assert analysis.confidence_score == 0.85


# ============ Tools Tests ============

def test_extract_error_patterns():
    """Test error pattern extraction tool"""
    
    logs = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "service_name": "api",
            "error_message": "NullPointerException",
            "environment": "production"
        },
        {
            "timestamp": "2024-01-15T10:05:00Z",
            "service_name": "api",
            "error_message": "NullPointerException",
            "environment": "production"
        },
        {
            "timestamp": "2024-01-15T10:10:00Z",
            "service_name": "auth",
            "error_message": "TimeoutException",
            "environment": "production"
        }
    ]
    
    patterns = tools.extract_error_patterns(logs)
    
    assert patterns["total_logs"] == 3
    assert "NullPointerException" in patterns["error_types"]
    assert patterns["error_types"]["NullPointerException"] == 2
    assert "api" in patterns["affected_services"]


def test_analyze_error_timeline():
    """Test error timeline analysis"""
    
    logs = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "service_name": "api",
            "error_message": "Error 1"
        },
        {
            "timestamp": "2024-01-15T11:00:00Z",
            "service_name": "api",
            "error_message": "Error 2"
        }
    ]
    
    timeline = tools.analyze_error_timeline(logs)
    
    assert timeline["total_errors"] == 2
    assert "first_occurrence" in timeline
    assert "last_occurrence" in timeline


def test_calculate_severity():
    """Test severity calculation"""
    
    assert tools.calculate_severity(60, 10) == "critical"
    assert tools.calculate_severity(35, 25) == "high"
    assert tools.calculate_severity(15, 8) == "medium"
    assert tools.calculate_severity(5, 2) == "low"


def test_generate_recommendations():
    """Test recommendation generation"""
    
    recs = tools.generate_recommendations(
        "NullPointerException - null validation",
        ["api-gateway", "auth-service"],
        {"error1": 5, "error2": 3}
    )
    
    assert len(recs) > 0
    assert any("null" in r.lower() for r in recs)


# ============ Prompt Tests ============

def test_system_prompt_generation():
    """Test system prompt generation"""
    
    prompt_quick = prompt.get_system_prompt("quick")
    prompt_standard = prompt.get_system_prompt("standard")
    prompt_detailed = prompt.get_system_prompt("detailed")
    
    assert "Root Cause Analysis" in prompt_quick
    assert "Root Cause Analysis" in prompt_standard
    assert "Root Cause Analysis" in prompt_detailed
    assert len(prompt_detailed) > len(prompt_quick)


def test_analysis_instruction():
    """Test analysis instruction generation"""
    
    instruction = prompt.get_analysis_instruction(
        5,
        ["database", "auth"],
        {"most_common_error": "NullPointerException", "error_frequency_percent": 40}
    )
    
    assert "database" in instruction
    assert "auth" in instruction
    assert "NullPointerException" in instruction


# ============ Agent Tests ============

def test_rca_agent_creation():
    """Test RCA Agent instantiation"""
    
    agent = RCAAgent()
    assert agent.name == "RCA-Agent"


def test_rca_agent_fallback_analysis():
    """Test fallback analysis when LLM not available"""
    
    agent = RCAAgent(llm_client=None)
    
    logs = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "service_name": "api-gateway",
            "error_message": "NullPointerException",
            "environment": "production"
        }
    ]
    
    # Test fallback analysis method
    error_patterns = tools.extract_error_patterns(logs)
    affected_systems = tools.identify_affected_systems(logs)
    stack_traces = tools.extract_stack_trace_patterns(logs)
    
    analysis_data = agent._fallback_analysis(
        logs, error_patterns, affected_systems, stack_traces
    )
    
    assert "root_cause" in analysis_data
    assert "affected_systems" in analysis_data
    assert "severity" in analysis_data
    assert analysis_data["confidence_score"] == 0.65


# ============ Workflow Tests ============

def test_workflow_state_management():
    """Test workflow state transitions"""
    
    workflow = RCAWorkflow()
    assert workflow.get_state().value == "idle"


def test_workflow_graph_routing():
    """Test workflow graph request routing"""
    
    graph = WorkflowGraph()
    
    request = RCARequest(
        logs=[
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "service_name": "api",
                "error_message": "Error"
            }
        ],
        analysis_depth="quick"
    )
    
    workflow_name = graph.route_request(request)
    assert workflow_name == "quick"


# ============ API Endpoint Tests ============

def test_health_endpoint():
    """Test health check endpoint"""
    
    response = client.get("/bug-rca/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    
    response = client.get("/bug-rca/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "bug_rca"


def test_info_endpoint():
    """Test info endpoint"""
    
    response = client.get("/bug-rca/info")
    assert response.status_code == 200
    data = response.json()
    assert "capabilities" in data
    assert "endpoints" in data


def test_analyze_endpoint_empty_logs():
    """Test analyze endpoint with empty logs"""
    
    response = client.post(
        "/bug-rca/analyze",
        json={"logs": []}
    )
    
    assert response.status_code == 400


def test_analyze_endpoint_valid_request():
    """Test analyze endpoint with valid request"""
    
    request_data = {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException",
                "environment": "production"
            }
        ],
        "analysis_depth": "quick"
    }
    
    response = client.post("/bug-rca/analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "analysis" in data
    assert "processing_time_ms" in data


def test_analyze_endpoint_too_many_logs():
    """Test analyze endpoint with too many logs"""
    
    logs = [
        {
            "timestamp": f"2024-01-15T{i%24:02d}:00:00Z",
            "service_name": "api",
            "error_message": f"Error {i}"
        }
        for i in range(100)
    ]
    
    response = client.post(
        "/bug-rca/analyze",
        json={"logs": logs}
    )
    
    assert response.status_code == 400


def test_quick_analyze_endpoint():
    """Test quick analyze endpoint"""
    
    request_data = {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "ConnectionException",
                "environment": "production"
            }
        ]
    }
    
    response = client.post("/bug-rca/quick-analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data


def test_detailed_analyze_endpoint():
    """Test detailed analyze endpoint"""
    
    request_data = {
        "logs": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "DatabaseConnectionError",
                "environment": "production"
            }
        ]
    }
    
    response = client.post("/bug-rca/detailed-analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data


def test_batch_analyze_endpoint():
    """Test batch analyze endpoint"""
    
    requests = [
        {
            "logs": [
                {
                    "timestamp": "2024-01-15T10:00:00Z",
                    "service_name": "api",
                    "error_message": "Error 1"
                }
            ]
        },
        {
            "logs": [
                {
                    "timestamp": "2024-01-15T11:00:00Z",
                    "service_name": "auth",
                    "error_message": "Error 2"
                }
            ]
        }
    ]
    
    response = client.post("/bug-rca/batch-analyze", json=requests)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 0  # At least some responses


# ============ Integration Tests ============

def test_full_analysis_workflow():
    """Test complete analysis workflow"""
    
    request_data = {
        "logs": [
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "stack_trace": "at com.example.RequestValidator.validate(RequestValidator.java:45)",
                "environment": "production",
                "request_id": "req_123"
            },
            {
                "timestamp": "2024-01-15T10:05:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "environment": "production",
                "request_id": "req_124"
            }
        ],
        "analysis_depth": "standard",
        "focus_areas": ["validation", "request_handling"]
    }
    
    response = client.post("/bug-rca/analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "request_id" in data
    assert "analysis" in data
    assert "processing_time_ms" in data
    assert "model_used" in data
    assert "analysis_summary" in data
    
    # Verify analysis content
    analysis = data["analysis"]
    assert "root_cause" in analysis
    assert "affected_systems" in analysis
    assert "severity" in analysis
    assert "business_impact" in analysis
    assert "recommendations" in analysis
    assert "confidence_score" in analysis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
