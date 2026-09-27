"""Collect the continuous 999.9 silver-bar certificate from the official IME API."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402

CONFIG = CertificateConfig(
    slug="silver", title_fa="گواهی سپرده پیوسته شمش نقره 999.9",
    commodity_id="21", contract_description="گواهی سپرده پیوسته شمش نقره 999.9",
    old_code="CD1SIB0001", new_code="SilverBar",
    csv_name="silver_certificate_raw.csv",
)

if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
