"""Core enumerations for TRACE forensic workstation."""
from enum import Enum


class NodeType(str, Enum):
    IP = "IP"
    WALLET = "Wallet"
    TRANSACTION = "Transaction"
    ENTITY = "Entity"
    CLUSTER = "Cluster"


class EdgeType(str, Enum):
    OBSERVED = "OBSERVED"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    COMMON_INPUT = "COMMON_INPUT"
    TRANSFER = "TRANSFER"
    ASSOCIATED = "ASSOCIATED"
    MEMBER_OF = "MEMBER_OF"


class PriorityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


class BehaviorPattern(str, Enum):
    NORMAL = "Normal Behavior"
    BURST = "Temporal Burst"
    FAN_IN = "High Fan-In Aggregation"
    FAN_OUT = "High Fan-Out Dispersion"
    CHAIN = "Rapid Multi-Hop Chain"
    MIXED = "Complex Mixing Pattern"
    DORMANT_ACTIVATION = "Dormant Activation"
    MULTI_IP = "Multi-IP Association"
    MULTI_COUNTRY = "Cross-Border / Multi-Country"
    HIGH_VELOCITY = "High Velocity Relaying"


class ValidationStatus(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    QUARANTINED = "Quarantined"
    DUPLICATE = "Duplicate"


class InvestigationStatus(str, Enum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    RESOLVED = "Resolved"
    ARCHIVED = "Archived"


class EvidenceStrength(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
