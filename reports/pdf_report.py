"""Local forensic PDF investigation report generator."""
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from core.constants import DISCLAIMER_TEXT

logger = logging.getLogger("TRACE.PDFReport")


class ForensicPDFReportGenerator:
    """Generates 12-section offline PDF investigation reports for law enforcement / intelligence analysts."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=6,
        )
        self.sub_title_style = ParagraphStyle(
            "DocSubTitle",
            parent=self.styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        )
        self.h2_style = ParagraphStyle(
            "SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=10,
            spaceAfter=4,
        )
        self.body_style = ParagraphStyle(
            "ReportBody",
            parent=self.styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )
        self.disclaimer_style = ParagraphStyle(
            "LegalDisclaimer",
            parent=self.styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748B"),
        )

    def generate_report(
        self,
        docket: Dict[str, Any],
        output_filepath: Path,
        dataset_meta: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Build and render PDF report."""
        output_filepath = Path(output_filepath)
        output_filepath.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_filepath),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        elements = []

        # Header Title
        elements.append(Paragraph("TRACE INVESTIGATIVE LEAD REPORT", self.title_style))
        elements.append(Paragraph(
            f"National Technical Research Organisation (NTRO) • Blockchain Forensics Workstation • Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            self.sub_title_style,
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=10))

        # 1. Executive Summary
        elements.append(Paragraph("1. Executive Summary", self.h2_style))
        ent_id = docket.get("entity_id", "Unknown")
        risk = docket.get("risk_score", 0.0)
        prio = docket.get("priority", "Low")
        conf = int(docket.get("confidence", 0.8) * 100)
        summary_text = (
            f"This dossier documents an investigative lead for entity <b>{ent_id}</b>. "
            f"Analytical risk synthesis assigned an operational priority of <b>{prio.upper()}</b> "
            f"(Risk Indicator: <b>{risk}/100</b>, Confidence: <b>{conf}%</b>). "
            f"Flags were raised primarily due to behavioral profile divergence, asymmetric flow ratios, "
            f"and associated network transmission observations."
        )
        elements.append(Paragraph(summary_text, self.body_style))

        # 2. Dataset Information
        elements.append(Paragraph("2. Dataset Information", self.h2_style))
        ds_name = dataset_meta.get("filename", "Bulk Offline Synthetic Feed") if dataset_meta else "Bulk Offline Synthetic Feed"
        elements.append(Paragraph(
            f"Source File: {ds_name} | Format: Offline Metadata Dataset | Environment: 100% Air-Gapped",
            self.body_style,
        ))

        # 3. Entity Information & Key Metrics Table
        elements.append(Paragraph("3. Entity Information", self.h2_style))
        data_table = [
            ["Entity ID", ent_id, "Classification", prio],
            ["Risk Indicator", f"{risk}/100", "Evidentiary Confidence", f"{conf}%"],
            ["Supervised Model Prob", f"{docket.get('model_probability', 0.0):.2f}", "Anomaly Score", f"{docket.get('anomaly_score', 0.0):.2f}"],
            ["Transaction Count", str(docket.get("transaction_count", 0)), "Behavioral Cluster ID", str(docket.get("cluster_id", -1))],
            ["Total Flow Out (BTC)", f"{docket.get('total_out_btc', 0.0):.4f}", "Total Flow In (BTC)", f"{docket.get('total_in_btc', 0.0):.4f}"],
        ]
        t = Table(data_table, colWidths=[130, 130, 130, 130])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 6))

        # 4. Risk Indicators & Reasons
        elements.append(Paragraph("4. Primary Risk Indicators", self.h2_style))
        reasons = docket.get("reasons", [])
        for r in reasons:
            elements.append(Paragraph(f"• {r}", self.body_style))

        # 5. Model Evidence & SHAP Attributions
        elements.append(Paragraph("5. Model Evidence (SHAP Feature Attributions)", self.h2_style))
        features = docket.get("top_contributing_features", [])
        if features:
            f_table_data = [["Feature", "Impact", "Direction", "Observed Value", "Forensic Meaning"]]
            for f in features[:5]:
                f_table_data.append([
                    f.get("feature", ""),
                    f"{f.get('impact', 0.0):+.3f}",
                    f.get("direction", ""),
                    f"{f.get('value', 0.0):.2f}",
                    Paragraph(f.get("description", ""), self.body_style),
                ])
            ft = Table(f_table_data, colWidths=[90, 50, 70, 60, 250])
            ft.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ]))
            elements.append(ft)
        else:
            elements.append(Paragraph("No anomalous feature attributions recorded.", self.body_style))

        # 6. Network Evidence
        elements.append(Paragraph("6. Network Layer Evidence", self.h2_style))
        ips = docket.get("associated_ips", [])
        ip_summary = f"Associated P2P Relay IPs ({len(ips)} observed): {', '.join(ips[:4]) if ips else 'None recorded'}"
        elements.append(Paragraph(ip_summary, self.body_style))

        # 7. Transaction Evidence
        elements.append(Paragraph("7. Blockchain Transaction Evidence", self.h2_style))
        elements.append(Paragraph(
            f"Total transactions: {docket.get('transaction_count', 0)} | Fan-Out: {docket.get('fan_out_ratio', 0.0):.2f} | Fan-In: {docket.get('fan_in_ratio', 0.0):.2f}",
            self.body_style,
        ))

        # 8. Graph Evidence & Chain
        elements.append(Paragraph("8. Graph Evidence Path", self.h2_style))
        chain = docket.get("evidence_chain", [])
        if chain:
            for step in chain:
                elements.append(Paragraph(
                    f"Step {step.get('step_number', 1)}: [{step.get('layer', '')}] {step.get('source', '')} --({step.get('relationship', '')})--> {step.get('target', '')}",
                    self.body_style,
                ))
        else:
            elements.append(Paragraph("Single-node or star topology without extended multi-hop chain.", self.body_style))

        # 9. Timeline & 10. Cluster Information
        elements.append(Paragraph("9. Timeline & 10. Cluster Information", self.h2_style))
        elements.append(Paragraph(
            f"Assigned to Behavioral Cluster #{docket.get('cluster_id', -1)}. "
            f"Velocity: {docket.get('velocity', 0.0):.2f} tx/hr | Burstiness: {docket.get('burstiness', 0.0):.2f}",
            self.body_style,
        ))

        # 11. Explanation Summary
        elements.append(Paragraph("11. Forensic Explanation", self.h2_style))
        elements.append(Paragraph(
            "Analytical signals cross-corroborate anomalous behavior. Multi-hop flow asymmetry combined with "
            "P2P network propagation anomalies warrants manual forensic examination.",
            self.body_style,
        ))

        # 12. Limitations & Statutory Disclaimers
        elements.append(Paragraph("12. Limitations & Statutory Disclaimer", self.h2_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
        elements.append(Paragraph(DISCLAIMER_TEXT, self.disclaimer_style))

        doc.build(elements)
        logger.info(f"Report generated successfully: {output_filepath}")
        return output_filepath
