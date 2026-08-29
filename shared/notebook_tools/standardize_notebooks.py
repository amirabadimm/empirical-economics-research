"""Install the governed dashboard section in every active commodity notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MARKER = "standard-market-dashboard-v1"
TARGETS = {
    "bitumen": ["01_bitumen_physical_analysis.ipynb"],
    "copper": ["01_lme_analysis.ipynb", "02_certificate_analysis.ipynb"],
    "pellet": ["01_physical_analysis.ipynb"],
    "rebar": ["01_physical_price_analysis.ipynb"],
    "zinc": ["01_zinc_analysis.ipynb", "02_bubble_analysis.ipynb"],
}
PHYSICAL_FILENAMES = {"copper": "copper_cathode_physical_raw.csv"}


def dashboard_cells(slug: str) -> list[nbformat.NotebookNode]:
    title = slug.title()
    markdown = nbformat.v4.new_markdown_cell(
        f"""## Standard market dashboard

This governed, read-only section uses the same presentation contract across commodity projects:
source coverage, physical and certificate activity, separate price panels, physical-goods
composition, and validated processed bubbles. It never writes raw data or constructs a missing
bubble. For {title}, product comparability still follows the project-specific workflow.""",
        metadata={"tags": [MARKER]},
    )
    code = nbformat.v4.new_code_cell(
        f"""from pathlib import Path
import sys

def locate_workspace(start=Path.cwd()):
    for candidate in [start, *start.parents]:
        if (candidate / "commodity" / "{slug}").exists() and (candidate / "shared").exists():
            return candidate
    raise FileNotFoundError("Could not locate workspace root")

WORKSPACE_ROOT = locate_workspace()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.notebook_tools.commodity_dashboard import (
    goods_type_counts,
    load_markets,
    market_summary,
    plot_available_bubbles,
    plot_goods_type_counts,
    plot_market_prices,
    plot_trade_activity,
)

PROJECT_DIR = WORKSPACE_ROOT / "commodity" / "{slug}"
physical_dashboard, certificate_dashboard = load_markets(
    PROJECT_DIR, "{slug}", physical_filename={PHYSICAL_FILENAMES.get(slug)!r}
)
display(market_summary(physical_dashboard, certificate_dashboard))
plot_trade_activity(physical_dashboard, certificate_dashboard, "{title}")
plot_market_prices(physical_dashboard, certificate_dashboard, "{title}")
goods_count_table = plot_goods_type_counts(physical_dashboard, "{title}", top_n=30)
display(goods_count_table)
bubble_series_plotted = plot_available_bubbles(PROJECT_DIR, "{title}")""",
        metadata={"tags": [MARKER]},
    )
    return [markdown, code]


def update(path: Path, slug: str) -> None:
    notebook = nbformat.read(path, as_version=4)
    notebook.cells = [
        cell for cell in notebook.cells if MARKER not in cell.get("metadata", {}).get("tags", [])
    ]
    notebook.cells.extend(dashboard_cells(slug))
    notebook.nbformat_minor = max(notebook.nbformat_minor, 5)
    nbformat.write(notebook, path)


def main() -> None:
    for slug, names in TARGETS.items():
        for name in names:
            path = WORKSPACE_ROOT / "commodity" / slug / "notebooks" / name
            update(path, slug)
            print(path.relative_to(WORKSPACE_ROOT))


if __name__ == "__main__":
    main()
