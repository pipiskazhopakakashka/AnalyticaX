"""
Application Configuration
Centralized configuration for the LLM Data Analyst system
"""

import os
from typing import Dict, Any
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR = BASE_DIR / "outputs"
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
for dir_path in [DATA_DIR, PROMPTS_DIR, OUTPUTS_DIR, CONFIG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_CONFIG = {
    "provider": "openai",  # Options: openai, anthropic, mock
    "model": "gpt-4-turbo-preview",
    "temperature": 0.3,
    "max_tokens": 2000,
    "api_key_env": "OPENAI_API_KEY"
}

# Mock LLM for development/demo
MOCK_LLM_ENABLED = os.getenv("USE_MOCK_LLM", "true").lower() == "true"

# Data Analysis Configuration
ANALYSIS_CONFIG = {
    "missing_threshold": 0.5,  # Max proportion of missing values allowed
    "correlation_threshold": 0.7,  # Threshold for strong correlation
    "anomaly_std_threshold": 3.0,  # Standard deviations for anomaly detection
    "trend_window": 7,  # Window size for trend calculation
    "top_n_insights": 10  # Number of top insights to generate
}

# Power BI Configuration
POWERBI_CONFIG = {
    "metadata_file": "powerbi_metadata.json",
    "kpi_threshold": {
        "critical": 0.1,  # 10% change considered critical
        "significant": 0.05  # 5% change considered significant
    }
}

# Chatbot Configuration
CHATBOT_CONFIG = {
    "max_history": 10,  # Number of conversation turns to maintain
    "context_window": 5,  # Number of previous messages to include
    "intent_confidence_threshold": 0.6
}

# Supported file formats
SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']

# Intent categories
INTENT_CATEGORIES = [
    "trend_analysis",
    "comparison",
    "explanation",
    "recommendation",
    "kpi_query",
    "dashboard_summary",
    "anomaly_detection",
    "general_query"
]

def get_config(section: str = None) -> Dict[str, Any]:
    """
    Get configuration for a specific section or all configuration
    
    Args:
        section: Configuration section name (llm, analysis, powerbi, chatbot)
        
    Returns:
        Configuration dictionary
    """
    config_map = {
        "llm": LLM_CONFIG,
        "analysis": ANALYSIS_CONFIG,
        "powerbi": POWERBI_CONFIG,
        "chatbot": CHATBOT_CONFIG
    }
    
    if section:
        return config_map.get(section, {})
    
    return {
        "llm": LLM_CONFIG,
        "analysis": ANALYSIS_CONFIG,
        "powerbi": POWERBI_CONFIG,
        "chatbot": CHATBOT_CONFIG,
        "paths": {
            "base": str(BASE_DIR),
            "data": str(DATA_DIR),
            "prompts": str(PROMPTS_DIR),
            "outputs": str(OUTPUTS_DIR)
        }
    }
