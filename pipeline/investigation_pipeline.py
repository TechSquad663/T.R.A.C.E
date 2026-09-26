"""Comprehensive offline forensic investigation pipeline orchestrator."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
import pandas as pd
import numpy as np

from core.models import TransactionRecord, Entity, Alert, DataQualityReportData
from core.enums import ValidationStatus, PriorityLevel, NodeType
from ingestion.csv_loader import load_csv_data
from ingestion.json_loader import load_json_data
from ingestion.xml_loader import load_xml_data
from ingestion.validator import DataValidator
from ingestion.normalizer import DataNormalizer
from ingestion.quality_report import QualityReporter
from correlation.network_blockchain import NetworkBlockchainCorrelator
from correlation.entity_resolution import EntityResolver
from graph.graph_builder import GraphBuilder
from graph.graph_features import GraphFeatureExtractor
from features.feature_pipeline import FeaturePipeline
from ml.model_manager import ModelManager
from scoring.risk_engine import RiskEngine
from scoring.confidence import ConfidenceCalculator
from scoring.alert_ranker import AlertRanker
from evidence.evidence_builder import EvidenceBuilder

logger = logging.getLogger("TRACE.Pipeline")


class InvestigationPipeline:
    """Master orchestrator executing the 14-stage forensic intelligence analysis."""

    def __init__(self):
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
        self.correlator = NetworkBlockchainCorrelator()
        self.entity_resolver = EntityResolver()
        self.graph_builder = GraphBuilder()
        self.feature_pipeline = FeaturePipeline()
        self.model_manager = ModelManager()
        self.risk_engine = RiskEngine()
        self.alert_ranker = AlertRanker()

        # State storage
        self.raw_records: List[Dict[str, Any]] = []
        self.records: List[TransactionRecord] = []
        self.quality_report: Optional[DataQualityReportData] = None
        self.entities: Dict[str, Entity] = {}
        self.graph = None
        self.graph_metrics: Dict[str, Dict[str, float]] = {}
        self.features_df: Optional[pd.DataFrame] = None
        self.alerts: List[Alert] = []
        self.evidence_builder: Optional[EvidenceBuilder] = None
        self.dockets: Dict[str, Dict[str, Any]] = {}
        self.evaluation_results: Dict[str, Any] = {}
        self.ground_truth: Optional[Dict[str, Dict[str, Any]]] = None

    def reset(self):
        """Reset internal pipeline state."""
        self.validator.reset()
        self.raw_records.clear()
        self.records.clear()
        self.entities.clear()
        self.graph = None
        self.graph_metrics.clear()
        self.features_df = None
        self.alerts.clear()
        self.dockets.clear()
        self.evaluation_results.clear()
        self.ground_truth = None

    def run_investigation(
        self,
        data_source: Union[str, Path, List[Dict[str, Any]]],
        ground_truth: Optional[Dict[str, Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute complete forensic investigation pipeline.
        Progress callback: callback(current_step, total_steps, status_message)
        """
        TOTAL_STEPS = 14
        self.ground_truth = ground_truth

        def update(step: int, msg: str):
            logger.info(f"Pipeline Step [{step}/{TOTAL_STEPS}]: {msg}")
            if progress_callback:
                progress_callback(step, TOTAL_STEPS, msg)

        # STAGE 1: Load Data
        update(1, "Loading dataset from offline source...")
        if isinstance(data_source, (str, Path)):
            p = Path(data_source)
            suffix = p.suffix.lower()
            file_size = p.stat().st_size if p.exists() else 0
            if suffix == ".csv":
                raw_data, err = load_csv_data(p)
                fmt = "CSV"
            elif suffix in [".json", ".jsonl"]:
                raw_data, err = load_json_data(p)
                fmt = "JSON"
            elif suffix == ".xml":
                raw_data, err = load_xml_data(p)
                fmt = "XML"
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
            if err:
                raise RuntimeError(f"Data loading failed: {err}")
            filename = p.name
        else:
            raw_data = data_source
            file_size = len(raw_data) * 200
            fmt = "IN_MEMORY"
            filename = "synthetic_memory_feed"

        self.raw_records = raw_data

        # STAGE 2: Validate Records
        update(2, f"Validating {len(raw_data)} records against canonical schema...")
        self.validator.reset()
        validated_list: List[TransactionRecord] = []
        invalid_count = 0
        quarantined_count = 0
        duplicate_count = 0
        all_errors: List[str] = []

        for raw_r in raw_data:
            status, errs = self.validator.validate_record(raw_r)
            if status == ValidationStatus.VALID:
                rec = self.normalizer.normalize_record(raw_r, status=status)
                validated_list.append(rec)
            elif status == ValidationStatus.DUPLICATE:
                duplicate_count += 1
                all_errors.extend(errs)
            elif status == ValidationStatus.QUARANTINED:
                quarantined_count += 1
                all_errors.extend(errs)
                rec = self.normalizer.normalize_record(raw_r, status=status, notes=errs)
                validated_list.append(rec)
            else:
                invalid_count += 1
                all_errors.extend(errs)

        self.records = [r for r in validated_list if r.validation_status == ValidationStatus.VALID]
        self.quality_report = QualityReporter.generate_report(
            filename=filename,
            file_format=fmt,
            file_size_bytes=file_size,
            validated_records=validated_list,
            invalid_count=invalid_count,
            quarantined_count=quarantined_count,
            duplicate_count=duplicate_count,
            validation_errors=all_errors,
        )

        if not self.records:
            raise ValueError("No valid records found in dataset to analyze.")

        # STAGE 3: Normalization
        update(3, f"Normalized {len(self.records)} canonical Bitcoin transaction records.")

        # STAGE 4: Network <-> Blockchain Correlation
        update(4, "Correlating P2P network observations with on-chain transactions...")
        net_corr = self.correlator.correlate(self.records)

        # STAGE 5: Entity Resolution & Common Input Ownership Heuristic
        update(5, "Resolving wallet entities via Common Input Ownership (CIO) heuristic...")
        self.entities = self.entity_resolver.resolve_entities(self.records)
        cio_links = self.entity_resolver.get_cio_relationships()

        # STAGE 6: Graph Construction
        update(6, "Constructing heterogeneous multi-directed transaction graph...")
        self.graph = self.graph_builder.build_graph(
            records=self.records,
            entities=self.entities,
            cio_links=cio_links,
        )
        self.evidence_builder = EvidenceBuilder(self.graph, self.model_manager)

        # STAGE 7: Graph Feature Extraction
        update(7, "Calculating graph centrality, PageRank, and topological metrics...")
        extractor = GraphFeatureExtractor(self.graph)
        self.graph_metrics = extractor.compute_all_metrics()

        # STAGE 8: Feature Pipeline Engineering
        update(8, "Synthesizing multi-modal behavioral, temporal, network, and graph features...")
        self.features_df = self.feature_pipeline.extract_features_for_entities(
            entities=self.entities,
            records=self.records,
            graph_metrics=self.graph_metrics,
        )

        # STAGE 9: Model Training / Inference (XGBoost, Isolation Forest, DBSCAN)
        update(9, "Executing supervised behavioral classifier (XGBoost)...")
        # Prepare training labels if ground truth is supplied, else self-train or use pre-existing
        y_train = None
        if self.ground_truth:
            y_train = np.array([
                1 if self.ground_truth.get(eid, {}).get("is_suspicious", 0) == 1
                or any(self.ground_truth.get(a, {}).get("is_suspicious", 0) == 1 for a in self.entities[eid].addresses)
                else 0
                for eid in self.features_df.index
            ])
            # Train if labels have variation
            if len(np.unique(y_train)) > 1:
                self.model_manager.train_and_save_all(self.features_df, y_train)

        # Run inference
        (
            model_probs,
            anomaly_scores,
            is_anomaly,
            cluster_labels,
            pca_coords,
            cluster_summaries,
        ) = self.model_manager.run_inference_pipeline(self.features_df)

        # STAGE 10: Isolation Forest Execution
        update(10, "Evaluating multivariate statistical deviation with Isolation Forest...")

        # STAGE 11: Behavioral Clustering
        update(11, "Clustering behavioral cohorts with DBSCAN...")

        # STAGE 12: SHAP & Tree Explainability
        update(12, "Generating SHAP feature attributions and evidentiary narratives...")
        combined_evidences = {}
        risk_evaluations = {}
        confidence_results = {}

        for idx, (ent_id, entity) in enumerate(self.entities.items()):
            row_feats = self.features_df.loc[ent_id]
            top_feats = self.model_manager.explainer.explain_instance(row_feats, top_k=5)

            # Store on entity
            entity.model_probability = float(model_probs[idx])
            entity.anomaly_score = float(anomaly_scores[idx])
            entity.cluster_id = int(cluster_labels[idx])
            entity.top_contributing_features = top_feats

            # Compute risk components
            graph_sig = self.risk_engine.compute_graph_signal(row_feats.to_dict())
            net_sig = self.risk_engine.compute_network_signal(row_feats.to_dict())
            risk_eval = self.risk_engine.evaluate_risk(
                model_prob=entity.model_probability,
                anomaly_score=entity.anomaly_score,
                graph_signal=graph_sig,
                network_signal=net_sig,
                raw_features=row_feats.to_dict(),
            )
            risk_evaluations[ent_id] = risk_eval
            entity.risk_score = risk_eval["risk_score"]
            entity.reasons = risk_eval["reasons"]

            # Confidence
            has_net = len(entity.ips) > 0
            conf, strength = ConfidenceCalculator.calculate_confidence_and_strength(
                model_prob=entity.model_probability,
                anomaly_score=entity.anomaly_score,
                tx_count=entity.transaction_count,
                supporting_records_count=entity.transaction_count,
                has_network_observation=has_net,
            )
            confidence_results[ent_id] = (conf, strength)
            entity.confidence = conf
            entity.priority = AlertRanker.determine_priority(entity.risk_score)

            # Multimodal evidence synthesis
            comb = self.model_manager.explainer.build_combined_evidence(
                entity_id=ent_id,
                model_prob=entity.model_probability,
                anomaly_score=entity.anomaly_score,
                top_features=top_feats,
                related_ips=entity.ips,
                related_txids=entity.txids,
                graph_evidence={
                    "degree": row_feats.get("graph_degree", 0),
                    "in_degree": row_feats.get("graph_in_degree", 0),
                    "out_degree": row_feats.get("graph_out_degree", 0),
                    "fan_in_ratio": row_feats.get("graph_fan_in_ratio", 0.0),
                    "fan_out_ratio": row_feats.get("graph_fan_out_ratio", 0.0),
                    "pagerank": row_feats.get("graph_pagerank", 0.0),
                    "total_flow_btc": entity.total_in + entity.total_out,
                },
                cluster_id=entity.cluster_id,
            )
            combined_evidences[ent_id] = comb

        # STAGE 13: Risk Fusion & Alert Ranking
        update(13, "Ranking investigative leads by forensic priority...")
        self.alerts = self.alert_ranker.rank_alerts(
            entities=self.entities,
            combined_evidences=combined_evidences,
            risk_evaluations=risk_evaluations,
            confidence_results=confidence_results,
        )

        # STAGE 14: Evidence Docket Generation
        update(14, "Assembling forensic evidence dossiers...")
        for ent_id, entity in self.entities.items():
            alert = next((a for a in self.alerts if a.entity_id == ent_id), None)
            docket = self.evidence_builder.build_docket(entity, alert, self.records)
            self.dockets[ent_id] = docket

        # Optional Model Evaluation if ground truth was supplied
        if self.ground_truth and y_train is not None and len(np.unique(y_train)) > 1:
            sup_eval = self.model_manager.evaluator.evaluate_detector(y_train, model_probs)
            ano_eval = self.model_manager.evaluator.evaluate_anomaly_detector(y_train, anomaly_scores, is_anomaly)
            self.evaluation_results = {
                "supervised": sup_eval,
                "unsupervised": ano_eval,
            }

        return {
            "status": "COMPLETED",
            "total_records": len(self.records),
            "total_entities": len(self.entities),
            "total_alerts": len(self.alerts),
            "high_priority_leads": sum(1 for a in self.alerts if a.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]),
            "graph_nodes": self.graph.number_of_nodes() if self.graph else 0,
            "graph_edges": self.graph.number_of_edges() if self.graph else 0,
        }
