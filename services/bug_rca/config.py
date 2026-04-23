"""
Configuration module for RCA Service
"""

import os
from typing import Optional


class RCAConfig:
    """Configuration for RCA Service"""
    
    # Service Configuration
    SERVICE_NAME = "bug_rca"
    SERVICE_VERSION = "1.0.0"
    SERVICE_DESCRIPTION = "Root Cause Analysis for Bug Logs"
    
    # Analysis Configuration
    MAX_LOGS_PER_REQUEST = 50
    DEFAULT_ANALYSIS_DEPTH = "standard"
    
    # LLM Configuration (optional)
    LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/default")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Timeout Configuration
    REQUEST_TIMEOUT_SECONDS = 30
    ANALYSIS_TIMEOUT_SECONDS = 25
    
    # Confidence Thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.5
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    
    @classmethod
    def get_llm_client(cls):
        """Get configured LLM client if available"""
        
        if cls.LLM_ENABLED:
            if cls.OPENROUTER_API_KEY:
                try:
                    from services.bug_rca.llm_clients import OpenRouterClient
                    return OpenRouterClient(
                        api_key=cls.OPENROUTER_API_KEY,
                        model=cls.OPENROUTER_MODEL
                    )
                except ImportError:
                    pass
            
            if cls.GEMINI_API_KEY:
                try:
                    from services.bug_rca.llm_clients import GeminiClient
                    return GeminiClient(
                        api_key=cls.GEMINI_API_KEY,
                        model=cls.GEMINI_MODEL
                    )
                except ImportError:
                    pass
        
        return None


# Severity level definitions
SEVERITY_LEVELS = {
    "critical": {"priority": 1, "description": "System-wide failure"},
    "high": {"priority": 2, "description": "Major service degradation"},
    "medium": {"priority": 3, "description": "Limited user impact"},
    "low": {"priority": 4, "description": "Isolated errors"}
}

# Analysis depth configurations
ANALYSIS_DEPTH_CONFIG = {
    "quick": {
        "max_processing_time_ms": 2000,
        "min_confidence": 0.7,
        "max_recommendations": 3
    },
    "standard": {
        "max_processing_time_ms": 5000,
        "min_confidence": 0.7,
        "max_recommendations": 5
    },
    "detailed": {
        "max_processing_time_ms": 10000,
        "min_confidence": 0.8,
        "max_recommendations": 8
    }
}
