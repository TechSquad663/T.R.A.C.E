"""CLI script to generate realistic synthetic Bitcoin transaction traffic datasets."""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator.synthetic_dataset import SyntheticBitcoinTrafficGenerator
from config.settings import get_settings


def main():
    parser = argparse.ArgumentParser(description="TRACE Synthetic Bitcoin Traffic Generator")
    parser.add_argument("--rows", type=int, default=1200, help="Number of transaction records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random generator seed for reproducibility")
    parser.add_argument("--format", type=str, choices=["csv", "json"], default="csv", help="Output file format")
    parser.add_argument("--output", type=str, default=None, help="Custom output path")
    args = parser.parse_args()

    settings = get_settings()
    out_dir = settings.SYNTHETIC_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    generator = SyntheticBitcoinTrafficGenerator(seed=args.seed)
    print(f"[*] Generating {args.rows} synthetic Bitcoin transactions (seed={args.seed})...")
    records, ground_truth = generator.generate_dataset(num_transactions=args.rows)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = out_dir / f"synthetic_traffic_{args.rows}_{args.seed}.{args.format}"

    gt_path = out_dir / f"ground_truth_{args.rows}_{args.seed}.json"

    if args.format == "csv":
        generator.export_csv(records, out_path)
    else:
        generator.export_json(records, out_path)

    generator.export_ground_truth(ground_truth, gt_path)

    print(f"[+] Dataset exported to: {out_path}")
    print(f"[+] Ground truth (isolated) saved to: {gt_path}")
    print(f"[+] Total transactions: {len(records)}")


if __name__ == "__main__":
    main()
