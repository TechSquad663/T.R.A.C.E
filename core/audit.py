"""Audit logging module for tracking chain-of-custody and analyst actions."""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime, timezone

logger = logging.getLogger("TRACE.Audit")

class AuditLogger:
    """Records analyst actions for chain-of-custody compliance."""
    
    def __init__(self, db_path: Path = Path("trace_audit.db")):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize audit database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    analyst_id TEXT,
                    action_type TEXT,
                    target_entity_id TEXT,
                    details_json TEXT
                )
            ''')
            conn.commit()
            
    def log_action(self, analyst_id: str, action_type: str, target_entity_id: str = "", details: Dict[str, Any] = None):
        """Log a specific action to the audit trail."""
        timestamp = datetime.now(timezone.utc).isoformat()
        if details is None:
            details = {}
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO audit_log (timestamp, analyst_id, action_type, target_entity_id, details_json) VALUES (?, ?, ?, ?, ?)',
                (timestamp, analyst_id, action_type, target_entity_id, json.dumps(details))
            )
            conn.commit()
            
        logger.info(f"Audit [{action_type}] by {analyst_id} on {target_entity_id}")
