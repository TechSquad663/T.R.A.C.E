"""SQLite persistence layer for TRACE."""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from core.models import TransactionRecord, Entity, Alert, InvestigationCase
from core.enums import PriorityLevel, InvestigationStatus

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

            # Investigation Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT,
                    subject_entity_id TEXT,
                    priority TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    analyst_notes TEXT,
                    attached_txids_json TEXT,
                    attached_alerts_json TEXT
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

    def save_case(self, case: InvestigationCase):
        """Save or update an individual investigation case docket."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cases
                (case_id, title, subject_entity_id, priority, status, created_at, updated_at, analyst_notes, attached_txids_json, attached_alerts_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case.case_id,
                case.title,
                case.subject_entity_id,
                case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                case.status.value if hasattr(case.status, 'value') else str(case.status),
                case.created_at,
                case.updated_at,
                case.analyst_notes,
                json.dumps(case.attached_txids),
                json.dumps(case.attached_alerts)
            ))
            conn.commit()

    def save_cases(self, cases: List[InvestigationCase]):
        """Bulk save investigation cases."""
        for c in cases:
            self.save_case(c)

    def load_cases(self) -> List[InvestigationCase]:
        """Load all saved investigation cases ordered by last update."""
        cases: List[InvestigationCase] = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT case_id, title, subject_entity_id, priority, status, created_at, updated_at, analyst_notes, attached_txids_json, attached_alerts_json
                FROM cases
                ORDER BY updated_at DESC
            ''')
            rows = cursor.fetchall()
            for r in rows:
                try:
                    c = InvestigationCase(
                        case_id=r[0],
                        title=r[1],
                        subject_entity_id=r[2],
                        priority=PriorityLevel(r[3]),
                        status=InvestigationStatus(r[4]),
                        created_at=r[5],
                        updated_at=r[6],
                        analyst_notes=r[7] or "",
                        attached_txids=json.loads(r[8]) if r[8] else [],
                        attached_alerts=json.loads(r[9]) if r[9] else []
                    )
                    cases.append(c)
                except Exception as err:
                    logger.warning(f"Error deserializing case {r[0]}: {err}")
        return cases

    def delete_case(self, case_id: str):
        """Remove a case docket from storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cases WHERE case_id = ?', (case_id,))
            conn.commit()
