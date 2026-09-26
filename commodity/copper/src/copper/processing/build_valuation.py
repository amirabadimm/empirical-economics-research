"""Build the three approved comparisons from one prepared input context."""
from pathlib import Path
from valuation_inputs import load_inputs
from build_certificate_bubble import build as build_primary
from build_intrinsic_bubbles import build as build_supporting


def build(project):
    prepared = load_inputs(project)
    primary = build_primary(project, prepared)
    physical, certificate = build_supporting(project, prepared)
    return primary, physical, certificate


if __name__ == '__main__':
    outputs = build(Path(__file__).resolve().parents[3])
    print('Approved comparison rows (primary, physical/intrinsic, certificate/intrinsic):',
          [len(rows) for rows in outputs])
