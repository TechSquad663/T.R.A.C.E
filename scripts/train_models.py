"""CLI script to train and persist offline ML model artifacts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from pipeline.investigation_pipeline import InvestigationPipeline
from config.settings import get_settings


def main():
    print("[*] Initializing offline model training...")
    settings = get_settings()
    generator = SyntheticBitcoinTrafficGenerator(seed=42)
    records, ground_truth = generator.generate_dataset(num_transactions=1500)

    pipeline = InvestigationPipeline()
    res = pipeline.run_investigation(records, ground_truth=ground_truth)

    print(f"[+] Model training completed.")
    print(f"[+] Artifacts saved to: {settings.MODELS_DIR}")
    print(f"[+] Analyzed {res['total_records']} transactions across {res['total_entities']} entities.")
    print(f"[+] Identified {res['high_priority_leads']} high-priority investigative leads.")


if __name__ == "__main__":
    main()
