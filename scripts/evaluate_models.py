"""CLI script to evaluate models and compute distribution-shift robustness metrics."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from pipeline.investigation_pipeline import InvestigationPipeline
from ml.evaluation import ModelEvaluator


def main():
    print("=" * 70)
    print("TRACE AI/ML FORENSIC MODEL EVALUATION")
    print("=" * 70)
    print("[*] Generating Baseline Scenario A (seed=42)...")
    gen_a = SyntheticBitcoinTrafficGenerator(seed=42)
    records_a, gt_a = gen_a.generate_dataset(num_transactions=1200, anomaly_ratio=0.20)

    pipe_a = InvestigationPipeline()
    res_a = pipe_a.run_investigation(records_a, ground_truth=gt_a)

    print("\n--- BASELINE EVALUATION (Scenario Set A) ---")
    sup_a = pipe_a.evaluation_results.get("supervised", {})
    ano_a = pipe_a.evaluation_results.get("unsupervised", {})

    print("Supervised Detector (XGBoost):")
    print(f"  • Precision : {sup_a.get('precision', 0.0):.4f}")
    print(f"  • Recall    : {sup_a.get('recall', 0.0):.4f}")
    print(f"  • F1-Score  : {sup_a.get('f1_score', 0.0):.4f}")
    print(f"  • ROC-AUC   : {sup_a.get('roc_auc', 0.0):.4f}")
    print(f"  • PR-AUC    : {sup_a.get('pr_auc', 0.0):.4f}")
    print(f"  • Confusion Matrix: {sup_a.get('confusion_matrix', {})}")

    print("\nAnomaly Detector (Isolation Forest):")
    print(f"  • Precision : {ano_a.get('precision', 0.0):.4f}")
    print(f"  • Recall    : {ano_a.get('recall', 0.0):.4f}")
    print(f"  • F1-Score  : {ano_a.get('f1_score', 0.0):.4f}")
    print(f"  • ROC-AUC   : {ano_a.get('roc_auc', 0.0):.4f}")

    print("\n[*] Evaluating Distribution Shift on Novel Parameter Scenario B (seed=999)...")
    gen_b = SyntheticBitcoinTrafficGenerator(seed=999)
    records_b, gt_b = gen_b.generate_dataset(num_transactions=1000, anomaly_ratio=0.30)

    pipe_b = InvestigationPipeline()
    res_b = pipe_b.run_investigation(records_b, ground_truth=gt_b)

    sup_b = pipe_b.evaluation_results.get("supervised", {})

    shift_res = ModelEvaluator.evaluate_distribution_shift(sup_a, sup_b)
    print("\n--- DISTRIBUTION-SHIFT GENERALIZATION METRICS ---")
    print(f"  • Baseline F1-Score   : {shift_res.get('baseline_f1', 0.0):.4f}")
    print(f"  • Shifted F1-Score    : {shift_res.get('shifted_f1', 0.0):.4f}")
    print(f"  • F1 Retention Rate   : {shift_res.get('f1_retention_rate', 0.0)}%")
    print(f"  • Performance Delta   : {shift_res.get('performance_delta_pct', 0.0)}%")
    print(f"  • Assessment          : {shift_res.get('generalization_assessment', '')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
