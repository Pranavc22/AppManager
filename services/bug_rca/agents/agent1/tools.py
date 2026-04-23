"""
Tools for RCA Agent - functions the agent can call
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime


def extract_error_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract common error patterns from multiple logs
    """
    error_types = {}
    services = set()
    environments = set()
    
    for log in logs:
        # Count error patterns
        error_msg = log.get("error_message", "")
        error_types[error_msg] = error_types.get(error_msg, 0) + 1
        services.add(log.get("service_name", "unknown"))
        environments.add(log.get("environment", "unknown"))
    
    # Find most common error
    most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else None
    
    return {
        "total_logs": len(logs),
        "error_types": error_types,
        "error_frequency": {k: (v/len(logs))*100 for k, v in error_types.items()},
        "affected_services": list(services),
        "affected_environments": list(environments),
        "most_common_error": most_common_error[0] if most_common_error else None,
        "error_frequency_percent": (most_common_error[1]/len(logs))*100 if most_common_error else 0
    }


def analyze_error_timeline(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze error distribution over time
    """
    # Sort logs by timestamp
    sorted_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    time_buckets = {}
    for log in sorted_logs:
        try:
            ts = log.get("timestamp", "")
            # Extract hour from timestamp
            hour = ts.split("T")[1].split(":")[0] if "T" in ts else "unknown"
            time_buckets[hour] = time_buckets.get(hour, 0) + 1
        except:
            time_buckets["unknown"] = time_buckets.get("unknown", 0) + 1
    
    return {
        "timeline": time_buckets,
        "first_occurrence": sorted_logs[-1].get("timestamp") if sorted_logs else None,
        "last_occurrence": sorted_logs[0].get("timestamp") if sorted_logs else None,
        "total_errors": len(logs)
    }


def identify_affected_systems(logs: List[Dict[str, Any]]) -> List[str]:
    """
    Identify all systems affected by the errors
    """
    services = set()
    for log in logs:
        service = log.get("service_name", "")
        if service:
            services.add(service)
    return sorted(list(services))


def calculate_severity(
    error_frequency: float,
    logs_count: int,
    has_critical_error: bool = False
) -> str:
    """
    Determine severity based on frequency and count
    """
    if has_critical_error or error_frequency > 50:
        return "critical"
    elif error_frequency > 30 or logs_count > 20:
        return "high"
    elif error_frequency > 10 or logs_count > 5:
        return "medium"
    else:
        return "low"


def extract_stack_trace_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract patterns from stack traces
    """
    stack_traces = {}
    locations = {}
    
    for log in logs:
        trace = log.get("stack_trace", "")
        if trace:
            stack_traces[trace] = stack_traces.get(trace, 0) + 1
            
            # Extract location hint
            try:
                if "at " in trace:
                    location = trace.split("at ")[1].split('\n')[0]
                    locations[location] = locations.get(location, 0) + 1
            except:
                pass
    
    return {
        "common_traces": stack_traces,
        "error_locations": locations,
        "most_common_location": max(locations.items(), key=lambda x: x[1])[0] if locations else None
    }


def assess_business_impact(
    affected_systems: List[str],
    severity: str,
    error_message: str
) -> str:
    """
    Assess business impact based on affected systems and severity
    """
    critical_systems = ["auth-service", "payment-service", "user-service", "api-gateway"]
    affected_critical = [s for s in affected_systems if s in critical_systems]
    
    if severity == "critical" and affected_critical:
        return f"CRITICAL: {len(affected_systems)} systems affected including critical {affected_critical[0]}. Service degradation for all users."
    elif severity == "high":
        return f"HIGH: {len(affected_systems)} systems impacted. {error_message[:50]}... Affecting subset of users."
    elif severity == "medium":
        return f"MEDIUM: {len(affected_systems)} system(s) with errors. Limited user impact."
    else:
        return f"LOW: {len(affected_systems)} system(s) with isolated errors."


def generate_recommendations(
    root_cause: str,
    affected_systems: List[str],
    error_types: Dict[str, int]
) -> List[str]:
    """
    Generate actionable recommendations based on analysis
    """
    recommendations = []
    
    # Add basic recommendations
    recommendations.append("Review recent code deployments for changes")
    
    # Add system-specific recommendations
    if "auth" in str(affected_systems).lower():
        recommendations.append("Check authentication service configuration and credentials")
    
    if "database" in str(root_cause).lower() or "connection" in str(root_cause).lower():
        recommendations.append("Verify database connection pool settings")
        recommendations.append("Check database health and availability")
    
    if "null" in str(root_cause).lower():
        recommendations.append("Add null-safety checks in affected code")
        recommendations.append("Implement input validation before processing")
    
    # Add monitoring recommendation
    recommendations.append("Add monitoring alerts for this error pattern")
    recommendations.append("Document root cause in incident tracking system")
    
    return recommendations


def format_analysis_summary(
    logs_count: int,
    root_cause: str,
    severity: str,
    confidence: float
) -> str:
    """
    Generate human-readable summary
    """
    return (
        f"Analyzed {logs_count} bug logs. "
        f"Root Cause: {root_cause}. "
        f"Severity: {severity.upper()}. "
        f"Confidence: {int(confidence*100)}%. "
        f"Immediate action recommended."
    )
