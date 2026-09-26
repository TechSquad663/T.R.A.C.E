"""SQLite persistence layer for TRACE."""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from core.models import TransactionRecord, Entity, Alert

logger = logging.getLogger("TRACE.Database")

class TRACEDatabase:
    """SQLite-backed persistence layer."""
    
    def __init__(self, db_path: Path = Path("trace_data.db")):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Entities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT,
                    addresses_json TEXT,
                    ips_json TEXT,
                    txids_json TEXT,
                    transaction_count INTEGER,
                    total_in REAL,
                    total_out REAL,
                    risk_score REAL,
                    confidence REAL,
                    priority TEXT,
                    cluster_id INTEGER,
                    reasons_json TEXT
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    entity_id TEXT,
                    entity_type TEXT,
                    risk_score REAL,
                    confidence REAL,
                    priority TEXT,
                    timestamp TEXT,
                    pattern TEXT,
                    reasons_json TEXT,
                    FOREIGN KEY(entity_id) REFERENCES entities(entity_id)
                )
            ''')
            
            # Quarantined records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quarantine (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_data_json TEXT,
                    errors_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
    def save_quarantined_record(self, raw_record: Dict[str, Any], errors: List[str]):
        """Save a quarantined record for manual review."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO quarantine (raw_data_json, errors_json) VALUES (?, ?)',
                (json.dumps(raw_record), json.dumps(errors))
            )
            conn.commit()

    def save_entities(self, entities: List[Entity]):
        """Bulk save entities."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            records = [
                (
                    e.entity_id,
                    e.entity_type.value,
                    json.dumps(e.addresses),
                    json.dumps(e.ips),
                    json.dumps(e.txids),
                    e.transaction_count,
                    e.total_in,
                    e.total_out,
                    e.risk_score,
                    e.confidence,
                    e.priority.value,
                    e.cluster_id,
                    json.dumps(e.reasons)
                )
                for e in entities
            ]
            cursor.executemany('''
                INSERT OR REPLACE INTO entities 
                (entity_id, entity_type, addresses_json, ips_json, txids_json, 
                 transaction_count, total_in, total_out, risk_score, confidence, 
                 priority, cluster_id, reasons_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            conn.commit()
            
    def save_alerts(self, alerts: List[Alert]):
        """Bulk save alerts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            records = [
                (
                    a.alert_id,
                    a.entity_id,
                    a.entity_type.value,
                    a.risk_score,
                    a.confidence,
                    a.priority.value,
                    a.timestamp,
                    a.pattern,
                    json.dumps(a.reasons)
                )
                for a in alerts
            ]
            cursor.executemany('''
                INSERT OR REPLACE INTO alerts 
                (alert_id, entity_id, entity_type, risk_score, confidence, priority, timestamp, pattern, reasons_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', records)
            conn.commit()
