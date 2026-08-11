"""Collect the continuous bitumen certificate from the official IME API."""

from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402

CONFIG = CertificateConfig(
    slug="bitumen", title_fa="گواهی سپرده پیوسته قیر", commodity_id="26",
    contract_description="گواهی سپرده پیوسته قیر",
    old_code="CD1BIT0001", new_code="Bitumen",
    csv_name="bitumen_certificate_raw.csv",
)

if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
