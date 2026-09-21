"""Install the standard bubble-distribution section in active analysis notebooks."""

from __future__ import annotations

from pathlib import Path

import nbformat


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MARKER = "standard-bubble-distribution-v1"
TARGETS = {
    "commodity/copper": ["notebooks/01_lme_analysis.ipynb", "notebooks/02_certificate_analysis.ipynb"],
    "commodity/zinc": ["notebooks/01_zinc_analysis.ipynb", "notebooks/02_bubble_analysis.ipynb"],
    "commodity/rebar": ["notebooks/01_physical_price_analysis.ipynb"],
    "commodity/pellet": ["notebooks/01_physical_analysis.ipynb"],
    "goods/pista": ["analysis/pista_certificate_analysis.ipynb"],
}


def distribution_cells(project_relative: str) -> list[nbformat.NotebookNode]:
    markdown = nbformat.v4.new_markdown_cell(
        """## Historical bubble distribution

This section reads the standardized processed table and renders an interactive Plotly figure for
each bubble type. The panels show the observed distribution, empirical cumulative distribution
function F(x), and magnitude frequency P(|Bubble| >= |x|). Negative bubbles retain their sign in
the first two panels; the third panel measures magnitude only.""",
        metadata={"tags": [MARKER]},
    )
    code = nbformat.v4.new_code_cell(
        f'''from pathlib import Path
import sys
import pandas as pd

def locate_distribution_workspace(start=Path.cwd()):
    for candidate in [start, *start.parents]:
        if (candidate / "shared").exists() and (candidate / "{project_relative}").exists():
            return candidate
    raise FileNotFoundError("Could not locate workspace root")

distribution_workspace = locate_distribution_workspace()
if str(distribution_workspace) not in sys.path:
    sys.path.insert(0, str(distribution_workspace))

from shared.market_analysis.bubble_distribution import plot_distribution_plotly

distribution_project = distribution_workspace / "{project_relative}"
distribution_files = list(
    (distribution_project / "data/processed/bubble").glob("*_bubble_distribution.csv")
)
if len(distribution_files) != 1:
    raise ValueError(f"Expected one named bubble distribution CSV, found {{distribution_files}}")
bubble_distribution = pd.read_csv(distribution_files[0], parse_dates=["observation_date"])
for series_id, series_distribution in bubble_distribution.groupby("series_id", sort=True):
    comparison = series_distribution["comparison"].iloc[0]
    figure = plot_distribution_plotly(series_distribution, comparison)
    figure.show()

display(bubble_distribution)''',
        metadata={"tags": [MARKER]},
    )
    return [markdown, code]


def update(path: Path, project_relative: str) -> None:
    notebook = nbformat.read(path, as_version=4)
    notebook.cells = [
        cell for cell in notebook.cells if MARKER not in cell.get("metadata", {}).get("tags", [])
    ]
    cleaned_cells = []
    section_number = 0
    for cell in notebook.cells:
        source = str(cell.get("source", "")).replace("�", "–").strip()
        if not source:
            continue
        if cell.cell_type == "markdown" and source.startswith("## "):
            import re

            match = re.match(r"^##\s+\d+\.\s+(.+)$", source.splitlines()[0])
            if match:
                section_number += 1
                first, *rest = source.splitlines()
                source = "\n".join([f"## {section_number}. {match.group(1)}", *rest])
        if project_relative == "goods/pista":
            source = source.replace("weekly Dahan-Bast proxy", "weekly Dahan-Bast observation")
            source = source.replace("# Pista certificate", "# Pistachio certificate")
        cell.source = source
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
        if cleaned_cells and cleaned_cells[-1].cell_type == cell.cell_type:
            if cleaned_cells[-1].source == cell.source:
                continue
        cleaned_cells.append(cell)
    notebook.cells = cleaned_cells
    notebook.cells.extend(distribution_cells(project_relative))
    notebook.nbformat_minor = max(notebook.nbformat_minor, 5)
    nbformat.write(notebook, path)


def main() -> None:
    for project_relative, notebooks in TARGETS.items():
        for notebook in notebooks:
            path = WORKSPACE_ROOT / project_relative / notebook
            update(path, project_relative)
            print(path.relative_to(WORKSPACE_ROOT))


if __name__ == "__main__":
    main()
