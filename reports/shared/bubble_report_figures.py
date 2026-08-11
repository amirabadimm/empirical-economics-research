"""Shared, headless figure builder for commodity bubble research reports."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


COLORS = {"physical": "#38598C", "certificate": "#A85D32", "main": "#2F7D63"}


def _load(path: Path, column: str) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["date", column])
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame.sort_values("date")


def _style(axis: plt.Axes, title: str) -> None:
    axis.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=10)
    axis.axhline(0, color="#222222", linewidth=0.9, alpha=0.8)
    axis.set_ylabel("Bubble (%)")
    axis.grid(axis="y", color="#D8DDE5", linewidth=0.7, alpha=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=9))
    axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(axis.xaxis.get_major_locator()))


def _single(frame: pd.DataFrame, column: str, title: str, color: str, output: Path) -> None:
    fig, axis = plt.subplots(figsize=(10.5, 4.3), constrained_layout=True)
    values = frame[column]
    axis.plot(frame["date"], values, color=color, linewidth=1.65)
    axis.fill_between(frame["date"], values, 0, where=values >= 0, color="#63A77B", alpha=0.20)
    axis.fill_between(frame["date"], values, 0, where=values < 0, color="#D16D6A", alpha=0.20)
    _style(axis, title)
    axis.text(
        0.995, 0.02,
        f"n={len(frame):,}  mean={values.mean():.2f}%  median={values.median():.2f}%",
        transform=axis.transAxes, ha="right", va="bottom", fontsize=9, color="#3F4752",
        bbox={"facecolor": "white", "edgecolor": "#D8DDE5", "alpha": 0.9, "pad": 4},
    )
    fig.savefig(output, dpi=220, facecolor="white")
    plt.close(fig)


def build(processed: Path, output: Path, commodity: str, main_filename: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    datasets = [
        ("physical_vs_intrinsic_bubble.csv", "physical_vs_intrinsic_bubble_pct", "Physical vs Intrinsic", "physical"),
        ("certificate_vs_intrinsic_bubble.csv", "certificate_vs_intrinsic_bubble_pct", "Certificate vs Intrinsic", "certificate"),
        (main_filename, "certificate_bubble_pct", "Certificate vs Estimated Physical", "main"),
    ]
    loaded = []
    for filename, column, label, key in datasets:
        frame = _load(processed / filename, column)
        loaded.append((frame, column, label, key))
        _single(frame, column, f"{commodity.title()}: {label}", COLORS[key], output / f"{commodity}_{key}_bubble.png")

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 10.0), constrained_layout=True)
    for axis, (frame, column, label, key) in zip(axes, loaded, strict=True):
        axis.plot(frame["date"], frame[column], color=COLORS[key], linewidth=1.35)
        _style(axis, label)
    fig.suptitle(f"{commodity.title()} Bubble Measures", fontsize=16, fontweight="bold", color="#17365D")
    fig.savefig(output / f"{commodity}_three_bubbles.png", dpi=220, facecolor="white")
    plt.close(fig)
    print(f"Wrote {commodity} report figures to {output}")
