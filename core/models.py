"""Core data models and forensic entities for TRACE."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from .enums import NodeType, PriorityLevel, ValidationStatus, InvestigationStatus, EvidenceStrength


@dataclass
class TransactionRecord:
    """Canonical Bitcoin transaction observation linking network and blockchain layers."""
    txid: str
    timestamp: str  # ISO-8601 string
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    input_addresses: List[str] = field(default_factory=list)
    output_addresses: List[str] = field(default_factory=list)
    input_amounts: List[float] = field(default_factory=list)
    output_amounts: List[float] = field(default_factory=list)
    fee: float = 0.0
    script_type: str = "P2PKH"
    geo_country: str = "Unknown"
    asn: str = "Unknown"
    
    # Internal metadata
    validation_status: ValidationStatus = ValidationStatus.VALID
    validation_notes: List[str] = field(default_factory=list)
    raw_record_id: Optional[str] = None
    
    @property
    def total_input_amount(self) -> float:
        return sum(self.input_amounts)
        
    @property
    def total_output_amount(self) -> float:
        return sum(self.output_amounts)
        
    @property
    def input_count(self) -> int:
        return len(self.input_addresses)
        
    @property
    def output_count(self) -> int:
        return len(self.output_addresses)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.txid,
            "timestamp": self.timestamp,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "input_addresses": self.input_addresses,
            "output_addresses": self.output_addresses,
            "input_amounts": self.input_amounts,
            "output_amounts": self.output_amounts,
            "fee": self.fee,
            "script_type": self.script_type,
            "geo_country": self.geo_country,
            "asn": self.asn,
            "validation_status": self.validation_status.value,
        }


@dataclass
class NetworkObservation:
    """Network-layer observation details."""
    observation_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    timestamp: str
    txid: str
    geo_country: str = "Unknown"
    asn: str = "Unknown"
    correlation_confidence: float = 1.0


@dataclass
class Entity:
    """Resolved entity (Wallet, Cluster, or IP)."""
    entity_id: str
    entity_type: NodeType
    addresses: List[str] = field(default_factory=list)
    ips: List[str] = field(default_factory=list)
    txids: List[str] = field(default_factory=list)
    
    # Behavioral and graph metrics
    transaction_count: int = 0
    total_in: float = 0.0
    total_out: float = 0.0
    velocity: float = 0.0
    burstiness: float = 0.0
    fan_in_ratio: float = 0.0
    fan_out_ratio: float = 0.0
    unique_counterparties: int = 0
    unique_ips: int = 0
    unique_countries: int = 0
    
    # Graph metrics
    degree: int = 0
    in_degree: int = 0
    out_degree: int = 0
    pagerank: float = 0.0
    betweenness: float = 0.0
    clustering_coeff: float = 0.0
    
    # AI/ML & Risk indicators
    model_probability: float = 0.0
    anomaly_score: float = 0.0
    cluster_id: int = -1
    risk_score: float = 0.0  # 0 to 100
    confidence: float = 0.0
    priority: PriorityLevel = PriorityLevel.LOW
    
    # Supporting explanations
    reasons: List[str] = field(default_factory=list)
    top_contributing_features: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def transactions(self) -> List[str]:
        return self.txids

    @property
    def relay_ips(self) -> List[str]:
        return self.ips

    @property
    def relay_countries(self) -> int:
        return self.unique_countries

    @property
    def detected_patterns(self) -> List[str]:
        return self.reasons

    @property
    def features(self) -> Dict[str, Any]:
        return {
            "transaction_count": self.transaction_count,
            "total_in": self.total_in,
            "total_out": self.total_out,
            "velocity": self.velocity,
            "burstiness": self.burstiness,
            "fan_in_ratio": self.fan_in_ratio,
            "fan_out_ratio": self.fan_out_ratio,
            "unique_counterparties": self.unique_counterparties,
            "unique_ips": self.unique_ips,
            "unique_countries": self.unique_countries,
            "degree": self.degree,
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "pagerank": self.pagerank,
            "betweenness": self.betweenness,
            "clustering_coeff": self.clustering_coeff,
            "anomaly_score": self.anomaly_score,
            "model_probability": self.model_probability,
            "cluster_id": self.cluster_id,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
        }



@dataclass
class Alert:
    """Ranked investigative lead."""
    alert_id: str
    entity_id: str
    entity_type: NodeType
    risk_score: float
    confidence: float
    priority: PriorityLevel
    timestamp: str
    pattern: str
    reasons: List[str] = field(default_factory=list)
    model_evidence: Dict[str, Any] = field(default_factory=dict)
    graph_evidence: Dict[str, Any] = field(default_factory=dict)
    network_evidence: Dict[str, Any] = field(default_factory=dict)
    transaction_evidence: Dict[str, Any] = field(default_factory=dict)
    related_transactions: List[str] = field(default_factory=list)
    related_ips: List[str] = field(default_factory=list)
    cluster_id: int = -1
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE


@dataclass
class InvestigationCase:
    """Analyst case folder for tracking leads and evidence."""
    case_id: str
    title: str
    subject_entity_id: str
    priority: PriorityLevel
    status: InvestigationStatus
    created_at: str
    updated_at: str
    analyst_notes: str = ""
    attached_txids: List[str] = field(default_factory=list)
    attached_alerts: List[str] = field(default_factory=list)


@dataclass
class DataQualityReportData:
    """Summary of data validation and ingestion quality."""
    filename: str
    file_format: str
    file_size_bytes: int
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    quarantined_records: int = 0
    duplicate_records: int = 0
    field_completeness: Dict[str, float] = field(default_factory=dict)
    error_summary: Dict[str, int] = field(default_factory=dict)
    timestamp: str = ""
