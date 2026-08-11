"""Maintain Zinc's local canonical USD/IRR input from the workspace TGJU collector.

The initial local copy is seeded byte-for-byte from the existing workspace
canonical history. Subsequent updates use the same TGJU close-price collector as
the Copper pipeline, but write atomically inside the Zinc domain.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.copper.src.copper.collectors.fx import update  # noqa: E402


def seed_if_missing(project_dir: Path) -> None:
    destination = project_dir / "data" / "raw" / "fx" / "usd_to_rial.csv"
    if destination.exists():
        return
    source = WORKSPACE_ROOT / "commodity" / "copper" / "data" / "raw" / "fx" / "usd_to_rial.csv"
    if not source.exists():
        raise FileNotFoundError(f"Workspace canonical USD history is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copyfile(source, temporary)
    temporary.replace(destination)


def main() -> None:
    project_dir = Path(__file__).resolve().parents[3]
    seed_if_missing(project_dir)
    update(project_dir)


if __name__ == "__main__":
    main()
