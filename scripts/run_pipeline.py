"""CLI script to run end-to-end investigation pipeline on a dataset file."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.investigation_pipeline import InvestigationPipeline
from reports.pdf_report import ForensicPDFReportGenerator
from config.settings import get_settings


def main():
    parser = argparse.ArgumentParser(description="Run TRACE Forensic Investigation Pipeline")
    parser.add_argument("dataset", type=str, help="Path to CSV, JSON, or XML dataset")
    parser.add_argument("--export-pdf", action="store_true", help="Generate PDF report for highest priority lead")
    args = parser.parse_args()

    input_path = Path(args.dataset)
    if not input_path.exists():
        print(f"[-] File not found: {input_path}")
        sys.exit(1)

    print(f"[*] Starting offline forensic pipeline on: {input_path.name}")
    pipeline = InvestigationPipeline()

    def on_progress(step, total, msg):
        print(f"  [{step:2d}/{total:2d}] {msg}")

    res = pipeline.run_investigation(input_path, progress_callback=on_progress)

    print("\n" + "=" * 60)
    print("INVESTIGATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Valid Transactions : {res['total_records']}")
    print(f"Resolved Entities        : {res['total_entities']}")
    print(f"Ranked Alerts Generated  : {res['total_alerts']}")
    print(f"High-Priority Leads      : {res['high_priority_leads']}")
    print(f"Graph Topology           : {res['graph_nodes']} nodes, {res['graph_edges']} edges")
    print("=" * 60)

    print("\nTOP 5 INVESTIGATIVE LEADS:")
    for a in pipeline.alerts[:5]:
        print(f"  • Alert {a.alert_id} | Entity: {a.entity_id[:16]} | Risk: {a.risk_score}/100 [{a.priority.value}] | Pattern: {a.pattern}")

    if args.export_pdf and pipeline.alerts:
        top_alert = pipeline.alerts[0]
        docket = pipeline.dockets[top_alert.entity_id]
        pdf_gen = ForensicPDFReportGenerator()
        out_pdf = get_settings().EXPORTS_DIR / f"Lead_Report_{top_alert.entity_id[:12]}.pdf"
        pdf_gen.generate_report(docket, out_pdf, {"filename": input_path.name})
        print(f"\n[+] PDF Lead Report written to: {out_pdf}")


if __name__ == "__main__":
    main()
