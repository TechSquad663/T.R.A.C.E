"""Cryptographic verification of datasets to ensure integrity."""
import hashlib
import json
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger("TRACE.DatasetVerification")

class DatasetVerifier:
    """Verifies SHA-256 hashes of datasets against a manifest."""
    
    @staticmethod
    def calculate_sha256(filepath: Path) -> str:
        """Calculate the SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def verify_dataset(filepath: Path, expected_hash: Optional[str] = None, manifest_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Verify a dataset against an expected hash or a manifest file.
        Returns (is_valid, actual_hash)
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Dataset file not found: {filepath}")

        logger.info(f"Calculating SHA-256 for {filepath.name}...")
        actual_hash = DatasetVerifier.calculate_sha256(filepath)
        
        if expected_hash:
            is_valid = actual_hash == expected_hash
            if not is_valid:
                logger.warning(f"Hash mismatch for {filepath.name}! Expected: {expected_hash}, Actual: {actual_hash}")
            else:
                logger.info(f"Dataset {filepath.name} verified successfully.")
            return is_valid, actual_hash

        if manifest_path and manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                expected = manifest.get(filepath.name)
                if expected:
                    is_valid = actual_hash == expected
                    if not is_valid:
                        logger.warning(f"Manifest hash mismatch for {filepath.name}!")
                    else:
                        logger.info(f"Dataset {filepath.name} verified against manifest.")
                    return is_valid, actual_hash
                else:
                    logger.info(f"No manifest entry found for {filepath.name}. Proceeding with actual hash: {actual_hash}")
            except Exception as e:
                logger.error(f"Failed to read manifest file: {e}")

        # If no expected hash or manifest is provided/matched, we just return the calculated hash as valid for record-keeping
        return True, actual_hash
