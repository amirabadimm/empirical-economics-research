"""Collect the continuous steel-rebar certificate from the official IME API."""

from pathlib import Path
import sys


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.ime_data.certificate_collector import CertificateConfig, run_cli  # noqa: E402


CONFIG = CertificateConfig(
    slug="rebar",
    title_fa="گواهی سپرده پیوسته میلگرد",
    commodity_id="29",
    contract_description="گواهی سپرده پیوسته میلگرد",
    old_code="CD1RBR0001",
    new_code="SteelRebar",
    csv_name="rebar_certificate_raw.csv",
)


if __name__ == "__main__":
    run_cli(Path(__file__).resolve().parents[3], CONFIG)
