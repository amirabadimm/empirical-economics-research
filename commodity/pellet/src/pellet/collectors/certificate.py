"""Collect the continuous iron-ore-pellet certificate from the official IME API."""

from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402

CONFIG = CertificateConfig(
    slug="pellet", title_fa="گواهی سپرده پیوسته گندله سنگ آهن", commodity_id="28",
    contract_description="گواهی سپرده پیوسته گندله سنگ آهن",
    old_code="CD1IOP0001", new_code="IronOrePlt",
    csv_name="pellet_certificate_raw.csv",
)

if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
