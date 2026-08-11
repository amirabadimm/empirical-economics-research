"""Collect the continuous zinc-ingot certificate from the official IME API."""

from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402

CONFIG = CertificateConfig(
    slug="zinc", title_fa="گواهی سپرده پیوسته شمش روی", commodity_id="30",
    contract_description="گواهی سپرده پیوسته شمش روی",
    old_code="CD1ZNI0001", new_code="ZincIngot",
    csv_name="zinc_certificate_raw.csv",
)

if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
