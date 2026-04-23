#!/usr/bin/env python
"""
One-Line Quick Tests for Bug RCA Service
Copy & paste to test immediately
"""

# ============================================================================
# OPTION 1: RUN EXISTING TEST SUITE (20+ tests)
# ============================================================================

# In terminal:
# pytest services/bug_rca/test_rca.py -v


# ============================================================================
# OPTION 2: QUICK API TEST (No setup needed, just copy-paste)
# ============================================================================

if __name__ == "__main__":
    import requests
    import json
    
    BASE_URL = "http://localhost:8000/bug-rca"
    
    print("=" * 70)
    print("🧪 RCA AGENT - QUICK TESTS")
    print("=" * 70)
    
    # TEST 1: Health Check
    print("\n1️⃣  Health Check")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {r.status_code} ✓" if r.status_code == 200 else f"   Status: {r.status_code} ✗")
        print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 Make sure service is running: python main.py")
    
    # TEST 2: Quick Analysis  
    print("\n2️⃣  Quick Analysis (1 error)")
    try:
        payload = {
            "logs": [{
                "timestamp": "2024-01-15T10:30:00Z",
                "service_name": "api-gateway",
                "error_message": "NullPointerException in RequestValidator",
                "environment": "production"
            }]
        }
        r = requests.post(f"{BASE_URL}/quick-analyze", json=payload)
        print(f"   Status: {r.status_code} ✓" if r.status_code == 200 else f"   Status: {r.status_code} ✗")
        if r.status_code == 200:
            data = r.json()
            print(f"   Root Cause: {data['analysis']['root_cause']}")
            print(f"   Severity: {data['analysis']['severity']}")
            print(f"   Time: {data['processing_time_ms']:.0f}ms")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # TEST 3: Standard Analysis (Multiple Errors)
    print("\n3️⃣  Standard Analysis (3 errors)")
    try:
        payload = {
            "logs": [
                {"timestamp": "2024-01-15T10:00:00Z", "service_name": "api", "error_message": "NullPointerException"},
                {"timestamp": "2024-01-15T10:05:00Z", "service_name": "api", "error_message": "NullPointerException"},
                {"timestamp": "2024-01-15T10:10:00Z", "service_name": "auth", "error_message": "TimeoutException"}
            ],
            "analysis_depth": "standard"
        }
        r = requests.post(f"{BASE_URL}/analyze", json=payload)
        print(f"   Status: {r.status_code} ✓" if r.status_code == 200 else f"   Status: {r.status_code} ✗")
        if r.status_code == 200:
            data = r.json()
            print(f"   Logs Analyzed: 3")
            print(f"   Affected Systems: {data['analysis']['affected_systems']}")
            print(f"   Confidence: {data['analysis']['confidence_score']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # TEST 4: Detailed Analysis  
    print("\n4️⃣  Detailed Analysis (Database Issue)")
    try:
        payload = {
            "logs": [
                {"timestamp": "2024-01-15T10:00:00Z", "service_name": "db", "error_message": "Connection pool exhausted"},
                {"timestamp": "2024-01-15T10:05:00Z", "service_name": "api", "error_message": "DatabaseConnectionError"}
            ],
            "analysis_depth": "detailed",
            "focus_areas": ["database", "connections"]
        }
        r = requests.post(f"{BASE_URL}/detailed-analyze", json=payload)
        print(f"   Status: {r.status_code} ✓" if r.status_code == 200 else f"   Status: {r.status_code} ✗")
        if r.status_code == 200:
            data = r.json()
            print(f"   Root Cause: {data['analysis']['root_cause']}")
            print(f"   Recommendations: {len(data['analysis']['recommendations'])} items")
            for i, rec in enumerate(data['analysis']['recommendations'][:3], 1):
                print(f"     {i}. {rec}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # TEST 5: Error Handling
    print("\n5️⃣  Error Handling (Empty Logs - Should Fail)")
    try:
        r = requests.post(f"{BASE_URL}/analyze", json={"logs": []})
        print(f"   Status: {r.status_code} ✓" if r.status_code == 400 else f"   Status: {r.status_code} ✗")
        print(f"   Expected Error: {r.json()['detail']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # TEST 6: Batch Analysis
    print("\n6️⃣  Batch Analysis (3 requests)")
    try:
        payload = [
            {"logs": [{"timestamp": "2024-01-15T10:00:00Z", "service_name": "api", "error_message": "Error 1"}]},
            {"logs": [{"timestamp": "2024-01-15T11:00:00Z", "service_name": "auth", "error_message": "Error 2"}]},
            {"logs": [{"timestamp": "2024-01-15T12:00:00Z", "service_name": "db", "error_message": "Error 3"}]}
        ]
        r = requests.post(f"{BASE_URL}/batch-analyze", json=payload)
        print(f"   Status: {r.status_code} ✓" if r.status_code == 200 else f"   Status: {r.status_code} ✗")
        if r.status_code == 200:
            results = r.json()
            print(f"   Requests: 3")
            print(f"   Successful: {len(results)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Quick tests complete! See results above.")
    print("=" * 70)
    print("\n📚 For more detailed testing:")
    print("   • Pytest:  pytest services/bug_rca/test_rca.py -v")
    print("   • Swagger: http://localhost:8000/docs")
    print("   • Guide:   services/bug_rca/TESTING_GUIDE.md")
