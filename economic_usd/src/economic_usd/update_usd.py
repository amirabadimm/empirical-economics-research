"""Refresh Iranian free-market USD/IRR from the same TGJU history used by the seed."""
import csv
import shutil
import subprocess
from datetime import date, datetime, timezone
from decimal import Decimal
from html.parser import HTMLParser

from .calendars import jalali_to_gregorian
from .io_utils import atomic_write
from .paths import RAW

URL = "https://www.tgju.org/profile/price_dollar_rl/history"
COLUMNS = ["date_pr", "date_gr", "source", "price_irr", "price_method"]


class HistoryParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.target = self.in_row = self.in_cell = False
        self.parts, self.row, self.rows = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tbody" and attrs.get("id") == "table-list": self.target = True
        elif self.target and tag == "tr": self.in_row, self.row = True, []
        elif self.in_row and tag == "td": self.in_cell, self.parts = True, []

    def handle_data(self, data):
        if self.in_cell: self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.in_cell:
            self.row.append("".join(self.parts).strip()); self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row: self.rows.append(self.row)
            self.in_row = False
        elif tag == "tbody" and self.target: self.target = False


def _download() -> bytes:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl: raise RuntimeError("curl is required")
    result = subprocess.run([curl, "-4", "-L", "--tlsv1.2", "--fail", "--silent", "--show-error", "--max-time", "90", "--user-agent", "Mozilla/5.0", URL], capture_output=True)
    if result.returncode or not result.stdout:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def _parse(content: bytes) -> list[dict[str, str]]:
    parser = HistoryParser(); parser.feed(content.decode("utf-8-sig"))
    rows = []
    for cells in parser.rows:
        if len(cells) != 8: raise ValueError(f"Unexpected TGJU row: {cells}")
        closing, gregorian, persian = cells[3], cells[6], cells[7]
        jy, jm, jd = map(int, persian.replace("-", "/").split("/"))
        calculated = jalali_to_gregorian(jy, jm, jd)
        published = date.fromisoformat(gregorian.replace("/", "-"))
        if calculated != published: raise ValueError(f"Calendar mismatch: {persian}")
        price = Decimal(closing.replace(",", ""))
        rows.append({"date_pr": f"{jy:04d}/{jm:02d}/{jd:02d}", "date_gr": f"{published.year}/{published.month}/{published.day}", "source": "tgju", "price_irr": f"{price:f}", "price_method": "close"})
    if not rows: raise ValueError("TGJU table was empty")
    return rows


def update() -> None:
    directory = RAW / "usd_free_market"
    seed = directory / "usd_to_rial_seed.csv"
    output = directory / "usd_to_rial.csv"
    source = output if output.exists() else seed
    with source.open(encoding="utf-8-sig", newline="") as handle:
        existing_rows = list(csv.DictReader(handle))
    existing = {r["date_pr"]: r for r in existing_rows}
    content = _download()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = directory / "snapshots" / f"tgju_usd_history_{stamp}.html"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(content)
    fetched = _parse(content)
    overlap = [r for r in fetched if r["date_pr"] in existing]
    conflicts = [r["date_pr"] for r in overlap if existing[r["date_pr"]]["price_irr"].replace(",", "") != r["price_irr"]]
    if conflicts:
        print(f"Notice: {len(conflicts)} visible overlapping TGJU dates revised to current published closes")
    existing.update({r["date_pr"]: r for r in fetched})
    ordered = [existing[k] for k in sorted(existing)]
    atomic_write(output, COLUMNS, ordered)
    print(f"USD source: TGJU free-market rial quote; visible={len(fetched)}, overlap={len(overlap)}, total={len(ordered)}, last={ordered[-1]['date_pr']}")


if __name__ == "__main__":
    update()

