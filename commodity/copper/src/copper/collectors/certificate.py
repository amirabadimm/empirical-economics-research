"""Collect the continuous copper-cathode certificate from the official IME API."""

from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402

CONFIG = CertificateConfig(
    slug="copper", title_fa="گواهی سپرده پیوسته مس کاتد", commodity_id="14",
    contract_description="گواهی سپرده پیوسته مس کاتد",
    old_code="CD1COP0001", new_code="CopperCthd",
    csv_name="copper_certificate_raw.csv",
)

if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
