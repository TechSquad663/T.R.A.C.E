"""Application configuration and settings for TRACE workstation."""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Settings:
    # Basic Application Metadata
    APP_NAME: str = "TRACE"
    APP_LONG_NAME: str = "TRACE — AI-Powered Bitcoin Traffic Forensic Intelligence Workstation"
    PROBLEM_STATEMENT: str = "SIH26146 — AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"
    ORGANIZATION: str = "National Technical Research Organisation (NTRO)"
    VERSION: str = "2.0.0-SIH26146"
    
    # Offline Enforcement
    OFFLINE_MODE: bool = True
    ALLOW_OUTBOUND_NETWORK: bool = False
    
    # Base Directories
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    DATA_DIR: Path = field(init=False)
    RAW_DATA_DIR: Path = field(init=False)
    PROCESSED_DATA_DIR: Path = field(init=False)
    SYNTHETIC_DATA_DIR: Path = field(init=False)
    MODELS_DIR: Path = field(init=False)
    GEOIP_DIR: Path = field(init=False)
    EXPORTS_DIR: Path = field(init=False)
    LOGS_DIR: Path = field(init=False)
    
    # Risk Fusion Weights (Must sum to 1.0)
    WEIGHT_MODEL_PROB: float = 0.35
    WEIGHT_ANOMALY_SCORE: float = 0.25
    WEIGHT_GRAPH_SIGNAL: float = 0.20
    WEIGHT_NETWORK_SIGNAL: float = 0.20
    
    # Anomaly & Clustering Settings
    IFOREST_CONTAMINATION: float = 0.08
    DBSCAN_EPS: float = 0.55
    DBSCAN_MIN_SAMPLES: int = 4
    
    # Entity Resolution / CIO
    CIO_MIN_TX_COUNT: int = 1
    CIO_CONFIDENCE_BASE: float = 0.75
    
    # UI Constants
    WINDOW_TITLE: str = "TRACE by Team TechSquad | SIH26146 Forensic Intelligence Workstation [OFFLINE]"
    DEFAULT_WINDOW_WIDTH: int = 1440
    DEFAULT_WINDOW_HEIGHT: int = 900
    THEME: str = "dark"
    
    def __post_init__(self):
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RAW_DATA_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DATA_DIR = self.DATA_DIR / "processed"
        self.SYNTHETIC_DATA_DIR = self.DATA_DIR / "synthetic"
        self.MODELS_DIR = self.DATA_DIR / "models"
        self.GEOIP_DIR = self.DATA_DIR / "geoip"
        self.EXPORTS_DIR = self.DATA_DIR / "exports"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        
        # Ensure directories exist
        for d in [
            self.DATA_DIR,
            self.RAW_DATA_DIR,
            self.PROCESSED_DATA_DIR,
            self.SYNTHETIC_DATA_DIR,
            self.MODELS_DIR,
            self.GEOIP_DIR,
            self.EXPORTS_DIR,
            self.LOGS_DIR,
        ]:
            d.mkdir(parents=True, exist_ok=True)


_settings_instance = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
