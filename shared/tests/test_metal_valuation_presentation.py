"""Read-only checks against the available local approved metal outputs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from shared.notebook_tools.commodity_dashboard import valuation_figures

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('metal', ['copper', 'zinc'])
def test_separate_approved_comparisons(metal):
    project = ROOT / 'commodity' / metal
    if not (project / f'data/processed/bubble/{metal}_certificate_bubble.csv').exists():
        pytest.skip('Local processed data required')
    figures = valuation_figures(project, metal.title())
    assert len(figures) == 3
    assert 'Primary' in figures[0].layout.title.text
    for fig in figures[1:]:
        assert 'Supporting' in fig.layout.title.text
        assert len(fig.data) == 1
    primary = pd.read_csv(project / f'data/processed/bubble/{metal}_certificate_bubble.csv').sort_values('date')
    np.testing.assert_allclose(figures[0].data[0].y, primary['certificate_bubble_pct'])
    assert all('regression' not in str(fig.to_plotly_json()).lower() for fig in figures)


@pytest.mark.parametrize('metal,name', [('copper','02_certificate_analysis'), ('zinc','02_bubble_analysis')])
def test_primary_precedes_research(metal, name):
    notebook = json.loads((ROOT / 'commodity' / metal / 'notebooks' / f'{name}.ipynb').read_text(encoding='utf8'))
    assert 'Primary result: certificate vs physical' in ''.join(notebook['cells'][0]['source'])
    assert 'Research appendix' in ''.join(notebook['cells'][6]['source'])
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            compile(''.join(cell['source']), f'{name}:{i}', 'exec')
