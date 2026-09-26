"""Data quality metrics and report generator for TRACE."""
from datetime import datetime, timezone
from typing import List, Dict, Any
from core.enums import ValidationStatus
from core.models import TransactionRecord, DataQualityReportData


class QualityReporter:
    """Computes forensic data quality summaries and validation health statistics."""

    @staticmethod
    def generate_report(
        filename: str,
        file_format: str,
        file_size_bytes: int,
        validated_records: List[TransactionRecord],
        invalid_count: int,
        quarantined_count: int,
        duplicate_count: int,
        validation_errors: List[str],
    ) -> DataQualityReportData:
        valid_count = sum(1 for r in validated_records if r.validation_status == ValidationStatus.VALID)
        total = valid_count + invalid_count + quarantined_count + duplicate_count

        # Compute field completeness on valid records
        field_completeness: Dict[str, float] = {}
        if validated_records:
            check_fields = [
                "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
                "txid", "input_addresses", "output_addresses", "input_amounts",
                "output_amounts", "fee", "script_type", "geo_country", "asn"
            ]
            for f in check_fields:
                present = 0
                for r in validated_records:
                    val = getattr(r, f, None)
                    if val is not None and val != "" and val != "Unknown" and val != []:
                        present += 1
                field_completeness[f] = round((present / len(validated_records)) * 100.0, 1)

        # Aggregate error occurrences
        error_summary: Dict[str, int] = {}
        for err in validation_errors:
            # Group error prefix
            prefix = err.split(":")[0] if ":" in err else err
            error_summary[prefix] = error_summary.get(prefix, 0) + 1

        return DataQualityReportData(
            filename=filename,
            file_format=file_format.upper(),
            file_size_bytes=file_size_bytes,
            total_records=total,
            valid_records=valid_count,
            invalid_records=invalid_count,
            quarantined_records=quarantined_count,
            duplicate_records=duplicate_count,
            field_completeness=field_completeness,
            error_summary=error_summary,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
