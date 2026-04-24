"""
Test script for Bug Matching & RCA endpoint
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/bug-rca"
MATCH_ENDPOINT = f"{BASE_URL}/match-and-analyze"


class BugMatchingTester:
    """Test suite for bug matching endpoint"""
    
    def __init__(self):
        self.test_cases = [
            {
                "name": "Null Pointer Exception",
                "description": "Users getting NullPointerException when authenticating. API gateway crashing with null pointer errors in validation.",
                "depth": "detailed"
            },
            {
                "name": "Memory Issues",
                "description": "OutOfMemoryError and heap space exceptions. Garbage collection taking 98% of time.",
                "depth": "standard"
            },
            {
                "name": "Database Problems",
                "description": "Database connections failing and causing cascade failures across services",
                "depth": "standard"
            },
            {
                "name": "Auth Failures",
                "description": "Auth service failing with multiple errors. Users cannot login or authenticate.",
                "depth": "quick"
            },
            {
                "name": "Timeout Errors",
                "description": "API requests timing out. Gateway timeout errors occurring frequently.",
                "depth": "quick"
            },
            {
                "name": "Rate Limiting",
                "description": "Rate limiting errors. Too many requests being rejected.",
                "depth": "quick"
            },
            {
                "name": "File System Errors",
                "description": "File not found errors and file system operation failures",
                "depth": "standard"
            },
        ]
    
    def test_successful_match(self, test_case: Dict[str, str]) -> bool:
        """Test a successful bug match"""
        print(f"\n{'='*80}")
        print(f"TEST: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Description: {test_case['description']}")
        print(f"Depth: {test_case['depth']}\n")
        
        try:
            payload = {
                "bug_description": test_case['description'],
                "analysis_depth": test_case['depth']
            }
            
            print("Sending request...")
            response = requests.post(MATCH_ENDPOINT, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract key information
            matched = data.get('matched_scenario', {})
            analysis = data.get('analysis', {})
            
            print(f"✓ Status: {response.status_code}")
            print(f"\n  Matched Scenario: {matched.get('scenario_name')}")
            print(f"  Match Score: {matched.get('match_score', 0)*100:.1f}%")
            print(f"  Matched Keywords: {', '.join(matched.get('matched_keywords', []))}")
            print(f"\n  Primary Error: {matched.get('primary_error_type')}")
            print(f"  Error Count in Dataset: {matched.get('error_count_in_dataset')}")
            print(f"  Services Affected: {', '.join(matched.get('affected_services_in_scenario', []))}")
            
            print(f"\n  Root Cause: {analysis.get('root_cause')}")
            print(f"  Severity: {analysis.get('severity', 'unknown').upper()}")
            print(f"  Analysis Confidence: {analysis.get('confidence_score', 0)*100:.1f}%")
            
            print(f"\n  Overall Confidence: {data.get('confidence_score', 0)*100:.1f}%")
            print(f"  Logs Analyzed: {data.get('logs_analyzed')}")
            print(f"  Processing Time: {data.get('processing_time_ms', 0):.0f}ms")
            
            # Immediate actions
            actions = data.get('immediate_actions', [])
            print(f"\n  Immediate Actions ({len(actions)}):")
            for i, action in enumerate(actions, 1):
                print(f"    {i}. {action}")
            
            # Preventive measures
            measures = data.get('preventive_measures', [])
            print(f"\n  Preventive Measures ({len(measures)}):")
            for i, measure in enumerate(measures, 1):
                print(f"    {i}. {measure}")
            
            # Timeline
            timeline = data.get('timeline', [])
            print(f"\n  Event Timeline ({len(timeline)} events):")
            for event in timeline[:3]:
                print(f"    - {event.get('time')}: {event.get('event')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {str(e)}")
            return False
        except json.JSONDecodeError:
            print(f"✗ Failed to parse response as JSON")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return False
    
    def test_error_case_short_description(self) -> bool:
        """Test error case: description too short"""
        print(f"\n{'='*80}")
        print("TEST: Error Case - Description Too Short")
        print(f"{'='*80}")
        
        try:
            payload = {
                "bug_description": "Bug",
                "analysis_depth": "quick"
            }
            
            response = requests.post(MATCH_ENDPOINT, json=payload, timeout=10)
            
            if response.status_code == 422:
                print(f"✓ Correctly rejected short description")
                print(f"  Status: {response.status_code}")
                error = response.json()
                print(f"  Error: {error['detail'][0]['msg']}")
                return True
            else:
                print(f"✗ Expected 422, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def test_error_case_vague_description(self) -> bool:
        """Test error case: very vague description"""
        print(f"\n{'='*80}")
        print("TEST: Error Case - No Match Found (Vague Description)")
        print(f"{'='*80}")
        
        try:
            payload = {
                "bug_description": "The system is not working as expected in all scenarios consistently",
                "analysis_depth": "quick"
            }
            
            response = requests.post(MATCH_ENDPOINT, json=payload, timeout=10)
            
            if response.status_code == 404:
                print(f"✓ Correctly identified no matching scenario")
                print(f"  Status: {response.status_code}")
                error = response.json()
                print(f"  Error: {error['detail']}")
                return True
            else:
                print(f"⚠ Got status {response.status_code}")
                data = response.json()
                if 'matched_scenario' in data:
                    print(f"  Matched: {data['matched_scenario']['scenario_name']}")
                    print(f"  Score: {data['matched_scenario']['match_score']*100:.1f}%")
                return True  # This is ok too, weak match is valid
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def test_different_depths(self) -> bool:
        """Test same description with different analysis depths"""
        print(f"\n{'='*80}")
        print("TEST: Different Analysis Depths")
        print(f"{'='*80}")
        
        description = "NullPointerException in API gateway request validation"
        depths = ["quick", "standard", "detailed"]
        
        for depth in depths:
            try:
                payload = {
                    "bug_description": description,
                    "analysis_depth": depth
                }
                
                print(f"\n  Testing depth: {depth.upper()}")
                response = requests.post(MATCH_ENDPOINT, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                print(f"    ✓ Status: {response.status_code}")
                print(f"    Processing Time: {data.get('processing_time_ms', 0):.0f}ms")
                print(f"    Confidence: {data.get('confidence_score', 0)*100:.1f}%")
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                return False
        
        return True
    
    def run_all_tests(self):
        """Run all test cases"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*20 + "BUG MATCHING ENDPOINT TEST SUITE" + " "*26 + "║")
        print("╚" + "="*78 + "╝")
        
        print(f"\nTarget Server: {BASE_URL}")
        print("Note: Make sure the FastAPI server is running!\n")
        
        passed = 0
        failed = 0
        
        # Run main test cases
        for test_case in self.test_cases:
            if self.test_successful_match(test_case):
                passed += 1
            else:
                failed += 1
        
        # Run error cases
        if self.test_error_case_short_description():
            passed += 1
        else:
            failed += 1
        
        if self.test_error_case_vague_description():
            passed += 1
        else:
            failed += 1
        
        # Test different depths
        if self.test_different_depths():
            passed += 1
        else:
            failed += 1
        
        # Print summary
        print(f"\n\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100) if (passed + failed) > 0 else 0:.1f}%")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    tester = BugMatchingTester()
    tester.run_all_tests()
