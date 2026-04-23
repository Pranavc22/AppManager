"""
Testing Guide for Bug RCA Service
Complete testing strategies and examples
"""

import requests
import json
from datetime import datetime, timedelta
import time


# ============================================================================
# METHOD 1: USING PYTEST (AUTOMATED TEST SUITE)
# ============================================================================

"""
Run all tests:
    pytest services/bug_rca/test_rca.py -v

Run specific test:
    pytest services/bug_rca/test_rca.py::test_health_endpoint -v

Run with coverage:
    pytest services/bug_rca/test_rca.py --cov

Run specific test class:
    pytest services/bug_rca/test_rca.py::TestSchemas -v

Run tests matching pattern:
    pytest services/bug_rca/test_rca.py -k "endpoint" -v

See test file for 20+ test cases covering:
  ✓ Schema validation
  ✓ Tool functions
  ✓ Prompt generation
  ✓ Agent analysis
  ✓ Workflow management
  ✓ API endpoints
  ✓ Integration workflows
"""


# ============================================================================
# METHOD 2: MANUAL API TESTING (cURL)
# ============================================================================

CURL_EXAMPLES = """
# 1. Health Check
curl -X GET http://localhost:8000/bug-rca/health

# 2. Service Info
curl -X GET http://localhost:8000/bug-rca/info

# 3. Quick Analysis
curl -X POST http://localhost:8000/bug-rca/quick-analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "logs": [{
      "timestamp": "2024-01-15T10:30:00Z",
      "service_name": "api-gateway",
      "error_message": "NullPointerException in RequestValidator",
      "environment": "production"
    }]
  }'

# 4. Standard Analysis
curl -X POST http://localhost:8000/bug-rca/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "logs": [{
      "timestamp": "2024-01-15T10:30:00Z",
      "service_name": "api-gateway",
      "error_message": "NullPointerException in RequestValidator",
      "stack_trace": "at com.example.RequestValidator.validate(RequestValidator.java:45)",
      "environment": "production",
      "request_id": "req_123"
    }],
    "analysis_depth": "standard",
    "focus_areas": ["validation", "request_handling"]
  }'

# 5. Detailed Analysis
curl -X POST http://localhost:8000/bug-rca/detailed-analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "logs": [{
      "timestamp": "2024-01-15T10:30:00Z",
      "service_name": "database-service",
      "error_message": "Connection timeout after 5000ms",
      "environment": "production"
    }]
  }'

# 6. Batch Analysis
curl -X POST http://localhost:8000/bug-rca/batch-analyze \\
  -H "Content-Type: application/json" \\
  -d '[
    {"logs": [{"timestamp": "2024-01-15T10:00:00Z", "service_name": "api", "error_message": "Error 1"}]},
    {"logs": [{"timestamp": "2024-01-15T11:00:00Z", "service_name": "auth", "error_message": "Error 2"}]}
  ]'

# 7. Too Many Logs (Should fail with 400)
curl -X POST http://localhost:8000/bug-rca/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "logs": [/* 60 entries */]
  }'

# 8. Empty Logs (Should fail with 400)
curl -X POST http://localhost:8000/bug-rca/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"logs": []}'
"""


# ============================================================================
# METHOD 3: PYTHON REQUESTS LIBRARY
# ============================================================================

class RCAAPITester:
    """Test RCA API using requests library"""
    
    BASE_URL = "http://localhost:8000/bug-rca"
    
    def __init__(self):
        self.session = requests.Session()
    
    def test_health(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        response = self.session.get(f"{self.BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    
    def test_info(self):
        """Test service info endpoint"""
        print("\n=== Testing Service Info ===")
        response = self.session.get(f"{self.BASE_URL}/info")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    
    def test_quick_analysis(self):
        """Test quick analysis"""
        print("\n=== Testing Quick Analysis ===")
        
        payload = {
            "logs": [
                {
                    "timestamp": "2024-01-15T10:30:00Z",
                    "service_name": "api-gateway",
                    "error_message": "NullPointerException in RequestValidator",
                    "environment": "production"
                }
            ],
            "analysis_depth": "quick"
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/analyze",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Request ID: {data['request_id']}")
            print(f"Root Cause: {data['analysis']['root_cause']}")
            print(f"Severity: {data['analysis']['severity']}")
            print(f"Confidence: {data['analysis']['confidence_score']}")
            print(f"Processing Time: {data['processing_time_ms']:.1f}ms")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_standard_analysis(self):
        """Test standard analysis with multiple logs"""
        print("\n=== Testing Standard Analysis ===")
        
        # Generate multiple related errors
        logs = [
            {
                "timestamp": f"2024-01-15T{i}:00:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "stack_trace": f"at com.example.RequestValidator.validate(RequestValidator.java:45)",
                "environment": "production",
                "request_id": f"req_{100+i}"
            }
            for i in range(3)
        ]
        
        payload = {
            "logs": logs,
            "analysis_depth": "standard",
            "focus_areas": ["validation", "null_safety"]
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/analyze",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Analyzed Logs: {len(logs)}")
            print(f"Root Cause: {data['analysis']['root_cause']}")
            print(f"Affected Systems: {data['analysis']['affected_systems']}")
            print(f"Severity: {data['analysis']['severity']}")
            print(f"Recommendations: {len(data['analysis']['recommendations'])}")
            print(f"Confidence: {data['analysis']['confidence_score']}")
            print(f"Processing Time: {data['processing_time_ms']:.1f}ms")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_detailed_analysis(self):
        """Test detailed analysis"""
        print("\n=== Testing Detailed Analysis ===")
        
        logs = [
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "service_name": "database-service",
                "error_message": "Connection pool exhausted",
                "environment": "production",
                "metadata": {"pool_size": 100, "active_connections": 105}
            },
            {
                "timestamp": "2024-01-15T10:05:00Z",
                "service_name": "database-service",
                "error_message": "Connection timeout after 5000ms",
                "environment": "production"
            }
        ]
        
        payload = {
            "logs": logs,
            "analysis_depth": "detailed",
            "focus_areas": ["database", "connections", "performance"]
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/detailed-analyze",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Root Cause: {data['analysis']['root_cause']}")
            print(f"Business Impact: {data['analysis']['business_impact']}")
            print(f"Recommendations ({len(data['analysis']['recommendations'])}):")
            for i, rec in enumerate(data['analysis']['recommendations'], 1):
                print(f"  {i}. {rec}")
            print(f"Processing Time: {data['processing_time_ms']:.1f}ms")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_batch_analysis(self):
        """Test batch analysis"""
        print("\n=== Testing Batch Analysis ===")
        
        requests_data = [
            {
                "logs": [{
                    "timestamp": "2024-01-15T10:00:00Z",
                    "service_name": "api-gateway",
                    "error_message": "NullPointerException"
                }]
            },
            {
                "logs": [{
                    "timestamp": "2024-01-15T11:00:00Z",
                    "service_name": "auth-service",
                    "error_message": "Invalid token validation"
                }]
            },
            {
                "logs": [{
                    "timestamp": "2024-01-15T12:00:00Z",
                    "service_name": "database-service",
                    "error_message": "Connection timeout"
                }]
            }
        ]
        
        response = self.session.post(
            f"{self.BASE_URL}/batch-analyze",
            json=requests_data
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Batch Size: {len(requests_data)}")
            print(f"Successful: {len(results)}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['analysis']['root_cause'][:50]}...")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n=== Testing Error Cases ===")
        
        # Test 1: Empty logs
        print("\n1. Empty Logs (expect 400)")
        response = self.session.post(
            f"{self.BASE_URL}/analyze",
            json={"logs": []}
        )
        print(f"   Status: {response.status_code} (expected 400)")
        
        # Test 2: Too many logs
        print("\n2. Too Many Logs (expect 400)")
        many_logs = [
            {
                "timestamp": f"2024-01-15T{i%24:02d}:00:00Z",
                "service_name": "api",
                "error_message": f"Error {i}"
            }
            for i in range(100)
        ]
        
        response = self.session.post(
            f"{self.BASE_URL}/analyze",
            json={"logs": many_logs}
        )
        print(f"   Status: {response.status_code} (expected 400)")
        
        # Test 3: Invalid analysis depth
        print("\n3. Invalid Analysis Depth (expect 422)")
        response = self.session.post(
            f"{self.BASE_URL}/analyze",
            json={
                "logs": [{"timestamp": "2024-01-15T10:00:00Z", "service_name": "api", "error_message": "Error"}],
                "analysis_depth": "invalid_depth"
            }
        )
        print(f"   Status: {response.status_code} (expected 422)")
        
        return True
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("=" * 70)
        print("RCA SERVICE - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        tests = [
            ("Health Check", self.test_health),
            ("Service Info", self.test_info),
            ("Quick Analysis", self.test_quick_analysis),
            ("Standard Analysis", self.test_standard_analysis),
            ("Detailed Analysis", self.test_detailed_analysis),
            ("Batch Analysis", self.test_batch_analysis),
            ("Error Cases", self.test_error_cases),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"\n❌ {test_name} FAILED: {str(e)}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return all(results.values())


# ============================================================================
# METHOD 4: DIRECT AGENT TESTING
# ============================================================================

def test_agent_directly():
    """Test RCA Agent directly without API"""
    print("\n=== Direct Agent Testing ===\n")
    
    from services.bug_rca.schemas.base_schema import RCARequest, BugLogEntry
    from services.bug_rca.agents.agent1.main import RCAAgent
    
    # Create agent
    agent = RCAAgent(llm_client=None)  # No LLM, uses fallback
    
    # Test 1: Single error
    print("Test 1: Single Error")
    request = RCARequest(
        logs=[
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException"
            }
        ]
    )
    
    response = agent.analyze(request)
    print(f"  Root Cause: {response.analysis.root_cause}")
    print(f"  Severity: {response.analysis.severity}")
    print(f"  Processing Time: {response.processing_time_ms:.1f}ms\n")
    
    # Test 2: Multiple related errors
    print("Test 2: Multiple Related Errors")
    request = RCARequest(
        logs=[
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "environment": "production"
            },
            {
                "timestamp": "2024-01-15T10:05:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "environment": "production"
            },
            {
                "timestamp": "2024-01-15T10:10:00Z",
                "service_name": "auth-service",
                "error_message": "AuthenticationException",
                "environment": "production"
            }
        ],
        analysis_depth="standard"
    )
    
    response = agent.analyze(request)
    print(f"  Root Cause: {response.analysis.root_cause}")
    print(f"  Affected Systems: {response.analysis.affected_systems}")
    print(f"  Severity: {response.analysis.severity}")
    print(f"  Recommendations: {len(response.analysis.recommendations)}")
    print(f"  Processing Time: {response.processing_time_ms:.1f}ms\n")
    
    # Test 3: Database error
    print("Test 3: Database Error Pattern")
    request = RCARequest(
        logs=[
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "service_name": "database-service",
                "error_message": "Connection pool exhausted",
                "metadata": {"pool_size": 100, "active": 105}
            },
            {
                "timestamp": "2024-01-15T10:02:00Z",
                "service_name": "api-gateway",
                "error_message": "DatabaseConnectionError: timeout"
            }
        ],
        analysis_depth="detailed",
        focus_areas=["database", "connections"]
    )
    
    response = agent.analyze(request)
    print(f"  Root Cause: {response.analysis.root_cause}")
    print(f"  Business Impact: {response.analysis.business_impact}")
    print(f"  Confidence: {response.analysis.confidence_score}")
    print(f"  Processing Time: {response.processing_time_ms:.1f}ms")


# ============================================================================
# METHOD 5: TOOLS TESTING
# ============================================================================

def test_tools_directly():
    """Test individual tools"""
    print("\n=== Testing Tools Directly ===\n")
    
    from services.bug_rca.agents.agent1 import tools
    
    logs = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "service_name": "api-gateway",
            "error_message": "NullPointerException",
            "stack_trace": "at com.example.Validator.validate(Validator.java:45)"
        },
        {
            "timestamp": "2024-01-15T10:05:00Z",
            "service_name": "api-gateway",
            "error_message": "NullPointerException",
            "stack_trace": "at com.example.Validator.validate(Validator.java:45)"
        },
        {
            "timestamp": "2024-01-15T10:10:00Z",
            "service_name": "auth-service",
            "error_message": "TimeoutException"
        }
    ]
    
    # Test 1: Extract patterns
    print("1. Extract Error Patterns:")
    patterns = tools.extract_error_patterns(logs)
    print(f"   Total Logs: {patterns['total_logs']}")
    print(f"   Unique Errors: {len(patterns['error_types'])}")
    print(f"   Affected Services: {patterns['affected_services']}")
    print(f"   Most Common: {patterns['most_common_error']} ({patterns['error_frequency_percent']:.0f}%)\n")
    
    # Test 2: Analyze timeline
    print("2. Error Timeline:")
    timeline = tools.analyze_error_timeline(logs)
    print(f"   First: {timeline['first_occurrence']}")
    print(f"   Last: {timeline['last_occurrence']}")
    print(f"   Timeline: {timeline['timeline']}\n")
    
    # Test 3: Affected systems
    print("3. Affected Systems:")
    systems = tools.identify_affected_systems(logs)
    print(f"   Systems: {systems}\n")
    
    # Test 4: Calculate severity
    print("4. Severity Calculation:")
    severity = tools.calculate_severity(error_frequency=60, logs_count=3)
    print(f"   Severity: {severity}\n")
    
    # Test 5: Business impact
    print("5. Business Impact Assessment:")
    impact = tools.assess_business_impact(
        ["api-gateway", "auth-service"],
        "high",
        "NullPointerException in validation"
    )
    print(f"   Impact: {impact}\n")
    
    # Test 6: Generate recommendations
    print("6. Recommendations:")
    recs = tools.generate_recommendations(
        "Null pointer in request validation",
        ["api-gateway", "auth-service"],
        patterns['error_types']
    )
    for i, rec in enumerate(recs, 1):
        print(f"   {i}. {rec}")


# ============================================================================
# MAIN - RUN TESTS
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("RCA AGENT - TESTING OPTIONS")
    print("=" * 70)
    
    print("""
1. PYTEST (Automated)
   pytest services/bug_rca/test_rca.py -v

2. API TESTING (Manual with cURL)
   curl -X GET http://localhost:8000/bug-rca/health

3. PYTHON REQUESTS (Interactive)
   python test_agent.py --api

4. DIRECT AGENT (No API)
   python test_agent.py --agent

5. TOOLS TESTING
   python test_agent.py --tools

6. ALL TESTS
   python test_agent.py --all

Choose an option or run individual tests below:
    """)
    
    arg = sys.argv[1] if len(sys.argv) > 1 else "--help"
    
    if arg == "--api":
        print("\nStarting API tests...")
        print("(Make sure services are running: python main.py)\n")
        tester = RCAAPITester()
        tester.run_all_tests()
    
    elif arg == "--agent":
        test_agent_directly()
    
    elif arg == "--tools":
        test_tools_directly()
    
    elif arg == "--all":
        print("\nRunning all tests...\n")
        test_agent_directly()
        test_tools_directly()
    
    else:
        print("""
Usage:
    python test_agent.py --api       # Test API endpoints
    python test_agent.py --agent     # Test agent directly
    python test_agent.py --tools     # Test tools
    python test_agent.py --all       # Run all test methods
        """)
