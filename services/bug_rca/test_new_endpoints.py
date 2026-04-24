"""
Test script for new RCA endpoints
Tests the dashboard and analyze-with-description endpoints
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DASHBOARD_ENDPOINT = f"{BASE_URL}/bug-rca/dashboard"
ANALYZE_WITH_DESC_ENDPOINT = f"{BASE_URL}/bug-rca/analyze-with-description"


def test_dashboard_endpoint():
    """Test the dashboard endpoint with different time windows"""
    print("\n" + "="*80)
    print("TEST 1: Dashboard Endpoint")
    print("="*80)
    
    time_windows = ["last_24h", "last_7d", "last_30d"]
    
    for window in time_windows:
        print(f"\n--- Testing with time_window: {window} ---")
        try:
            response = requests.get(
                DASHBOARD_ENDPOINT,
                params={"time_window": window},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Print statistics
            stats = data.get("statistics", {})
            print(f"✓ Status: {response.status_code}")
            print(f"  Total Incidents: {stats.get('total_incidents', 'N/A')}")
            print(f"  High-Risk Incidents: {stats.get('high_risk_incidents', 'N/A')}")
            print(f"  Low-Risk Incidents: {stats.get('low_risk_incidents', 'N/A')}")
            print(f"  Most Common Error: {stats.get('most_common_error', 'N/A')}")
            
            # Print questions
            questions = data.get("questions", [])
            print(f"\n  Pre-populated Questions ({len(questions)}):")
            for q in questions:
                print(f"    - {q.get('question')}")
                print(f"      Value: {q.get('current_value')} | Trend: {q.get('trend')}")
            
            # Print insights
            insights = data.get("insights", [])
            print(f"\n  Insights ({len(insights)}):")
            for insight in insights[:3]:  # Show first 3
                print(f"    - {insight}")
            
            # Print investigations
            investigations = data.get("suggested_investigations", [])
            print(f"\n  Suggested Investigations ({len(investigations)}):")
            for inv in investigations[:3]:  # Show first 3
                print(f"    - {inv}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Failed to connect to {DASHBOARD_ENDPOINT}")
            print("  Make sure the FastAPI server is running on port 8000")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {str(e)}")
        except json.JSONDecodeError:
            print(f"✗ Failed to parse response as JSON")


def test_analyze_with_description():
    """Test the analyze-with-description endpoint"""
    print("\n" + "="*80)
    print("TEST 2: Full RCA Analysis Endpoint (analyze-with-description)")
    print("="*80)
    
    # Test Case 1: Service Down Issue
    print("\n--- Test Case 1: Service Down Issue ---")
    request_payload = {
        "issue_description": "API Gateway service went down for 30 minutes. Users unable to authenticate due to null pointer exceptions in the request validation layer. Multiple timeout errors observed.",
        "issue_type": "service_down",
        "affected_service": "api-gateway",
        "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
        "end_time": datetime.utcnow().isoformat() + "Z",
        "affected_users_count": 5000,
        "analysis_depth": "detailed"
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            ANALYZE_WITH_DESC_ENDPOINT,
            json=request_payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"  Request ID: {data.get('request_id')}")
        print(f"  Issue Summary: {data.get('issue_summary')[:100]}...")
        
        # Print analysis
        analysis = data.get("analysis", {})
        print(f"\n  Root Cause Analysis:")
        print(f"    Root Cause: {analysis.get('root_cause')}")
        print(f"    Severity: {analysis.get('severity').upper()}")
        print(f"    Confidence: {analysis.get('confidence_score')*100:.0f}%")
        
        # Print affected services
        services = data.get("affected_services", [])
        print(f"\n  Affected Services ({len(services)}):")
        for service in services:
            print(f"    - {service}")
        
        # Print immediate actions
        actions = data.get("immediate_actions", [])
        print(f"\n  Immediate Actions ({len(actions)}):")
        for action in actions:
            print(f"    - {action}")
        
        # Print preventive measures
        measures = data.get("preventive_measures", [])
        print(f"\n  Preventive Measures ({len(measures)}):")
        for measure in measures:
            print(f"    - {measure}")
        
        # Print timeline
        timeline = data.get("timeline", [])
        print(f"\n  Event Timeline ({len(timeline)} events):")
        for event in timeline[:3]:  # Show first 3
            print(f"    - {event.get('time')}: {event.get('event')}")
        
        print(f"\n  Processing Time: {data.get('processing_time_ms'):.0f}ms")
        print(f"  Model Used: {data.get('model_used')}")
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Failed to connect to {ANALYZE_WITH_DESC_ENDPOINT}")
        print("  Make sure the FastAPI server is running on port 8000")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {str(e)}")
    except json.JSONDecodeError:
        print(f"✗ Failed to parse response as JSON")
    
    # Test Case 2: Performance Issue (minimal payload)
    print("\n--- Test Case 2: Performance Issue (Minimal Payload) ---")
    request_payload = {
        "issue_description": "Database queries running 10x slower than normal. Search feature experiencing timeout errors.",
        "issue_type": "performance",
        "affected_service": "search-service",
        "analysis_depth": "standard"
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            ANALYZE_WITH_DESC_ENDPOINT,
            json=request_payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✓ Status: {response.status_code}")
        print(f"  Request ID: {data.get('request_id')}")
        
        analysis = data.get("analysis", {})
        print(f"  Root Cause: {analysis.get('root_cause')}")
        print(f"  Severity: {analysis.get('severity').upper()}")
        print(f"  Logs Analyzed: {data.get('logs_analyzed')}")
        print(f"  Processing Time: {data.get('processing_time_ms'):.0f}ms")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {str(e)}")
    except json.JSONDecodeError:
        print(f"✗ Failed to parse response as JSON")


def validate_response_structure(response_data: Dict[str, Any], endpoint_name: str):
    """Validate response structure"""
    print(f"\nValidating {endpoint_name} response structure...")
    
    required_fields = {
        "dashboard": ["statistics", "questions", "insights", "suggested_investigations"],
        "analyze": ["request_id", "issue_summary", "analysis", "logs_analyzed", "immediate_actions", "preventive_measures"]
    }
    
    fields = required_fields.get(endpoint_name, [])
    missing = [f for f in fields if f not in response_data]
    
    if missing:
        print(f"  ✗ Missing fields: {missing}")
        return False
    else:
        print(f"  ✓ All required fields present")
        return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "RCA ENDPOINTS TEST SUITE" + " "*34 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\nTarget Server: {BASE_URL}")
    print("Note: Make sure FastAPI server is running before executing tests!")
    
    # Run tests
    test_dashboard_endpoint()
    test_analyze_with_description()
    
    print("\n" + "="*80)
    print("Test Suite Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
