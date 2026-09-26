"""Model evaluation suite computing real test metrics, confusion matrices, and distribution shift performance."""
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
)

logger = logging.getLogger("TRACE.Evaluation")


class ModelEvaluator:
    """Evaluates behavioral detection models on holdout synthetic validation sets."""

    @staticmethod
    def evaluate_detector(
        y_true: np.ndarray,
        y_prob: np.ndarray,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Compute real, un-fabricated classification metrics for supervised detector."""
        if len(y_true) == 0 or len(np.unique(y_true)) < 2:
            return {
                "status": "UNAVAILABLE",
                "message": "Evaluation requires labeled test scenarios with both normal and anomalous classes.",
            }

        y_pred = (y_prob >= threshold).astype(int)

        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            roc_auc = 0.0

        try:
            precision_pts, recall_pts, _ = precision_recall_curve(y_true, y_prob)
            pr_auc = float(auc(recall_pts, precision_pts))
        except Exception:
            pr_auc = 0.0

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

        return {
            "status": "VALIDATED",
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            "threshold": threshold,
            "test_sample_count": len(y_true),
        }

    @staticmethod
    def evaluate_anomaly_detector(
        y_true: np.ndarray,
        anomaly_scores: np.ndarray,
        is_anomaly_pred: np.ndarray,
    ) -> Dict[str, Any]:
        """Compute metrics for unsupervised Isolation Forest against ground truth."""
        if len(y_true) == 0 or len(np.unique(y_true)) < 2:
            return {
                "status": "UNAVAILABLE",
                "message": "Evaluation requires labeled ground truth scenarios.",
            }

        y_pred = is_anomaly_pred.astype(int)
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        try:
            roc_auc = float(roc_auc_score(y_true, anomaly_scores))
        except Exception:
            roc_auc = 0.0

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

        return {
            "status": "VALIDATED",
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            "test_sample_count": len(y_true),
        }

    @staticmethod
    def evaluate_distribution_shift(
        baseline_eval: Dict[str, Any],
        shifted_eval: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate performance drop across distribution shift scenarios
        (e.g., training on standard parameter burst/fanout and testing on novel parameter variants).
        """
        if baseline_eval.get("status") != "VALIDATED" or shifted_eval.get("status") != "VALIDATED":
            return {"status": "UNAVAILABLE", "message": "Both baseline and shifted test sets required."}

        f1_base = baseline_eval["f1_score"]
        f1_shifted = shifted_eval["f1_score"]
        drop_pct = round(((f1_base - f1_shifted) / max(0.001, f1_base)) * 100.0, 2)

        return {
            "status": "VALIDATED",
            "baseline_f1": f1_base,
            "shifted_f1": f1_shifted,
            "f1_retention_rate": round((f1_shifted / max(0.001, f1_base)) * 100.0, 1),
            "performance_delta_pct": drop_pct,
            "generalization_assessment": (
                "Robust cross-distribution generalization" if drop_pct < 15.0
                else "Moderate parameter sensitivity — recommendation: retrain with broader scenario variance"
            ),
        }
