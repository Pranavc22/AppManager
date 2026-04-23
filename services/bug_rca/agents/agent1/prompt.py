"""
Prompt templates and instructions for RCA Agent
"""


def get_system_prompt(analysis_depth: str = "standard") -> str:
    """
    System prompt for RCA agent based on analysis depth
    """
    
    base_prompt = """You are an expert Root Cause Analysis (RCA) agent specializing in analyzing bug logs from production systems.

Your responsibilities:
1. Analyze error logs to identify root causes
2. Assess impact on business and systems
3. Provide actionable recommendations
4. Map system dependencies and ripple effects
5. Assign appropriate severity levels

Key principles:
- Be precise and data-driven
- Focus on business impact
- Consider system dependencies
- Identify patterns across errors
- Provide specific, actionable recommendations"""

    depth_configurations = {
        "quick": {
            "description": "quick analysis",
            "guidelines": """
Analysis Style: Quick and focused
- Identify most likely root cause
- List top 2-3 affected systems
- Severity: focus on critical/high
- 2-3 key recommendations
- Aim for 0.7+ confidence (prioritize speed)
Time target: <2 seconds"""
        },
        "standard": {
            "description": "balanced analysis",
            "guidelines": """
Analysis Style: Thorough and balanced
- Detailed root cause explanation
- All affected systems mapped
- Full business impact assessment
- 4-5 comprehensive recommendations
- Include related error patterns
- Aim for 0.7-0.9 confidence
Time target: 2-5 seconds"""
        },
        "detailed": {
            "description": "comprehensive analysis",
            "guidelines": """
Analysis Style: In-depth comprehensive analysis
- Multi-factor root cause analysis
- Complete system dependency mapping
- Detailed business and technical impact
- Prevention strategies and long-term solutions
- Historical context if identifiable
- 5+ detailed recommendations
- Implementation guidance
- Aim for 0.8-1.0 confidence with proper context
Time target: 5-10 seconds"""
        }
    }
    
    config = depth_configurations.get(analysis_depth, depth_configurations["standard"])
    
    return f"""{base_prompt}

{config['guidelines']}"""


def get_analysis_instruction(
    logs_count: int,
    focus_areas: list = None,
    error_patterns: dict = None
) -> str:
    """
    Specific analysis instruction for given logs
    """
    
    focus_text = ""
    if focus_areas:
        focus_text = f"FOCUS AREAS: {', '.join(focus_areas)}\nPrioritize analysis on these specific areas."
    
    patterns_text = ""
    if error_patterns:
        most_common = error_patterns.get("most_common_error", "")
        frequency = error_patterns.get("error_frequency_percent", 0)
        patterns_text = f"\nMost common error appears in {frequency:.1f}% of logs: {most_common}"
    
    return f"""Analyze the following {logs_count} bug log(s) and provide Root Cause Analysis.

{focus_text}{patterns_text}

REQUIRED OUTPUT FORMAT (JSON):
{{
    "root_cause": "string - the primary root cause identified",
    "affected_systems": ["list", "of", "affected", "systems"],
    "severity": "critical|high|medium|low",
    "business_impact": "string - specific business implications",
    "recommendations": ["array", "of", "specific", "actionable", "recommendations"],
    "confidence_score": 0.85,
    "related_errors": ["list", "of", "related", "patterns"]
}}

Return ONLY valid JSON, no other text."""


def format_logs_for_analysis(logs: list) -> str:
    """
    Format bug logs into readable text for analysis
    """
    
    formatted_logs = []
    for i, log in enumerate(logs, 1):
        log_text = f"""
Log #{i}:
  Timestamp: {log.get('timestamp', 'N/A')}
  Service: {log.get('service_name', 'N/A')}
  Error: {log.get('error_message', 'N/A')}
  Environment: {log.get('environment', 'N/A')}
  Stack Trace: {log.get('stack_trace', 'Not provided')}
  Request ID: {log.get('request_id', 'N/A')}
"""
        formatted_logs.append(log_text)
    
    return "\n".join(formatted_logs)


def get_json_parse_instruction() -> str:
    """
    Instruction for parsing JSON from LLM response
    """
    
    return """
If the response contains a JSON code block (```json...```), extract the JSON from it.
Otherwise, extract the complete JSON object from the response.
Ensure all required fields are present:
  - root_cause
  - affected_systems
  - severity
  - business_impact
  - recommendations
  - confidence_score
"""
