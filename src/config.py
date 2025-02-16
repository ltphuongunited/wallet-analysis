from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# API Configuration
API_CONFIG = {
    "etherscan": {
        "url": "https://api.etherscan.io/api",
        "key": os.getenv("ETHERSCAN_KEY"),
    },
    "gemini": {
        "model": "gemini-pro",
        "key": os.getenv("GEMINI_KEY"),
    }
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "time_periods": [30, 90, 180],  # Days to analyze for trends
    "transaction_size_thresholds": {
        "large": 100000,
        "medium": 10000
    },
    "wallet_age_categories": {
        "veteran": 5,     # years
        "established": 2,
        "intermediate": 1
    }
}

def get_wallet_data_path(wallet_address: str) -> Path:
    """Get path for wallet data file"""
    return DATA_DIR / f"wallet_data_{wallet_address}.json"

def get_report_path(wallet_address: str) -> Path:
    """Get path for wallet report file"""
    return REPORTS_DIR / f"report_{wallet_address}.txt" 