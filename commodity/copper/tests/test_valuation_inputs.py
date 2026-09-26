"""Local regression protection for the consolidated valuation builders."""
import csv
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src/copper/processing'))
import build_certificate_bubble as primary
import build_intrinsic_bubbles as supporting
from valuation_inputs import load_inputs
from shared.certificate_pipeline.refresh import convert


def test_builders_match_canonical_outputs_without_writing():
    if not (PROJECT / 'data/raw/certificate/copper_certificate_raw.csv').exists():
        pytest.skip('Local copper inputs required')
    context = load_inputs(PROJECT)
    with patch.object(primary, 'write_atomic'), patch.object(supporting, 'write_atomic'):
        main = primary.build(PROJECT, context)
        physical, certificate = supporting.build(PROJECT, context)
    for rows, filename in [(main, 'copper_certificate_bubble.csv'),
                           (physical, 'physical_vs_intrinsic_bubble.csv'),
                           (certificate, 'certificate_vs_intrinsic_bubble.csv')]:
        with (PROJECT / 'data/processed/bubble' / filename).open(encoding='utf-8-sig') as f:
            assert rows == list(csv.DictReader(f))


def example():
    return {'date': '2026-09-01', 'certificate_price_irr_per_kg': '110',
            'estimated_physical_price_irr_per_kg': '100',
            'certificate_bubble_irr_per_kg': '10.000', 'certificate_bubble_pct': '10.000'}


def test_export_preserves_canonical_representation():
    result = convert('copper', 'primary', example())
    assert result['premium_discount_pct'] == '10.000'
    assert result['spread_irr_per_kg'] == '10.000'


def test_export_rejects_inconsistent_result():
    with pytest.raises(ValueError, match='Inconsistent canonical'):
        convert('copper', 'primary', example() | {'certificate_bubble_pct': '11'})
