"""One-time, source-preserving notebook presentation migration."""
import json
from pathlib import Path


def cell(kind, source):
    result = {"cell_type": kind, "metadata": {}, "source": source.splitlines(True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def main():
    root = Path(__file__).resolve().parents[2]
    for metal, filename in [("copper", "02_certificate_analysis.ipynb"),
                            ("zinc", "02_bubble_analysis.ipynb")]:
        path = root / "commodity" / metal / "notebooks" / filename
        notebook = json.loads(path.read_text(encoding="utf-8"))
        if "Primary result: certificate vs physical" in "".join(notebook["cells"][0]["source"]):
            continue
        setup = f'''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display

WORKSPACE = next(p for p in [Path.cwd(), *Path.cwd().parents]
                 if (p / 'shared').is_dir() and (p / 'commodity/{metal}').is_dir())
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))
from shared.notebook_tools.commodity_dashboard import valuation_figures, PLOTLY_CONFIG
PROJECT = WORKSPACE / 'commodity/{metal}'
approved_primary = pd.read_csv(PROJECT / 'data/processed/bubble/{metal}_certificate_bubble.csv', parse_dates=['date'])
figures = valuation_figures(PROJECT, '{metal.title()}')
figures[0].show(config=PLOTLY_CONFIG)
values = approved_primary['certificate_bubble_pct']
display(pd.DataFrame([{{'Observations': len(values), 'From': approved_primary['date'].min(),
    'To': approved_primary['date'].max(), 'Mean (%)': values.mean(),
    'Median (%)': values.median(), 'Latest (%)': approved_primary.sort_values('date')['certificate_bubble_pct'].iloc[-1]}}]))
'''
        intro = f'''# {metal.title()} certificate valuation
## Primary result: certificate vs physical

The objective is to measure the certificate premium or discount to the domestic physical benchmark.
The main chart uses the approved bounded, interpolated physical-to-intrinsic ratio method:
**100 × (certificate price / estimated physical price − 1)**.
Dots identify observed physical anchors; the remaining eligible dates use the approved interpolation.
Positive values indicate a premium; negative values indicate a discount.

Sources: IME certificate and physical transactions, Westmetall LME quotations, and the shared free-market USD/IRR series.
This presentation reads existing processed outputs; refresh the project before reviewing it.
'''
        front = [cell("markdown", intro), cell("code", setup),
                 cell("markdown", "## Supporting result: certificate vs intrinsic\n\nIntrinsic reference = LME cash USD/kg × USD/IRR. This is a separate comparison, not the primary certificate-to-physical bubble."),
                 cell("code", "figures[1].show(config=PLOTLY_CONFIG)"),
                 cell("markdown", "## Supporting result: physical vs intrinsic\n\nThis chart measures the domestic physical-market premium or discount to the same international reference."),
                 cell("code", "figures[2].show(config=PLOTLY_CONFIG)"),
                 cell("markdown", "## Reading the results\n\nUse the first chart for the main certificate-to-physical comparison. The next two charts provide international-value context and are not interchangeable with it. Statistics above are calculated from the loaded data rather than copied into prose.\n\n---\n# Research appendix — supporting work and experimental methods\n\nThe following work records how the benchmark and alternative methods were investigated. Experimental regressions do not replace the approved primary result above.")]
        old = notebook["cells"]
        if metal == "copper":
            old[0] = cell("markdown", "## Historical regression investigation\n\nResearch record only: the approved result is presented above. The later intrinsic-only regression supersedes the early two-feature experiment within this appendix.")
        else:
            old[0] = cell("markdown", "## Benchmark construction and diagnostics\n\nThese supporting diagnostics read processed datasets. Regression remains experimental.")
            old[4] = cell("markdown", "### Comparison definitions\n\nThe three approved comparisons are shown separately at the start of this notebook.")
            old[5] = cell("code", "# Independent approved comparison charts are displayed above.")
        for c in old:
            if c["cell_type"] == "code":
                text = "".join(c["source"])
                text = text.replace('bubble_series_plotted = plot_available_bubbles(PROJECT_DIR, "' + metal.title() + '")', '# Approved comparison charts are displayed at the start of this notebook.')
                c["source"] = text.splitlines(True)
                c["outputs"] = []
                c["execution_count"] = None
        notebook["cells"] = front + old
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
