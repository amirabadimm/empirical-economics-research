"""Standard empirical distributions for computed commodity bubble series."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT_COLUMNS = [
    "commodity",
    "bubble_type",
    "point_type",
    "point_method",
    "is_interpolated",
    "series_id",
    "comparison",
    "source_file",
    "observation_date",
    "bubble_pct",
    "empirical_cdf",
    "percentile",
    "abs_exceedance_probability",
    "abs_exceedance_pct",
    "observation_count",
]


@dataclass(frozen=True)
class BubbleSeriesSpec:
    """Explicit mapping from one governed bubble output to the standard schema."""

    series_id: str
    bubble_type: str
    comparison: str
    source_file: str
    date_column: str
    bubble_column: str
    exact_filter_column: str | None = None
    exact_filter_value: str | int | float | None = None
    point_method_column: str | None = None


def _atomic_csv(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig")
    temporary.replace(destination)


def empirical_distribution(
    source: pd.DataFrame, *, commodity: str, spec: BubbleSeriesSpec
) -> pd.DataFrame:
    """Return exact empirical CDF and absolute-magnitude exceedance values."""
    required = {spec.date_column, spec.bubble_column}
    if spec.exact_filter_column:
        required.add(spec.exact_filter_column)
    if spec.point_method_column:
        required.add(spec.point_method_column)
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"{spec.source_file} missing columns: {sorted(missing)}")

    exact_source = source
    if spec.exact_filter_column:
        filter_values = source[spec.exact_filter_column]
        if isinstance(spec.exact_filter_value, (int, float)):
            mask = pd.to_numeric(filter_values, errors="coerce").eq(spec.exact_filter_value)
        else:
            mask = filter_values.astype("string").eq(str(spec.exact_filter_value))
        exact_source = source.loc[mask]

    frame = pd.DataFrame(
        {
            "observation_date": pd.to_datetime(
                exact_source[spec.date_column], errors="coerce"
            ),
            "bubble_pct": pd.to_numeric(exact_source[spec.bubble_column], errors="coerce"),
        }
    ).dropna()
    if frame.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    if frame["observation_date"].duplicated().any():
        raise ValueError(f"Duplicate observation dates in {spec.source_file}")

    count = len(frame)
    frame["empirical_cdf"] = frame["bubble_pct"].rank(method="max", pct=True)
    frame["percentile"] = frame["empirical_cdf"] * 100
    frame["abs_exceedance_probability"] = (
        frame["bubble_pct"].abs().rank(method="max", ascending=False, pct=True)
    )
    frame["abs_exceedance_pct"] = frame["abs_exceedance_probability"] * 100
    if spec.point_method_column:
        point_method = exact_source.loc[frame.index, spec.point_method_column].astype("string")
        frame["point_method"] = point_method
        frame["is_interpolated"] = point_method.str.contains(
            "interpol", case=False, na=False
        )
        frame["point_type"] = np.where(
            frame["is_interpolated"], "interpolated", "observed"
        )
    else:
        frame["point_method"] = "observed"
        frame["is_interpolated"] = False
        frame["point_type"] = "observed"
    frame["commodity"] = commodity
    frame["bubble_type"] = spec.bubble_type
    frame["series_id"] = spec.series_id
    frame["comparison"] = spec.comparison
    frame["source_file"] = spec.source_file
    frame["observation_count"] = count
    return frame[OUTPUT_COLUMNS].sort_values(["bubble_pct", "observation_date"])


def _histogram_bins(values: pd.Series) -> int:
    if len(values) < 2 or values.nunique() == 1:
        return 1
    edges = np.histogram_bin_edges(values, bins="fd")
    return max(5, min(60, len(edges) - 1))


def plot_distribution(frame: pd.DataFrame, destination: Path, title: str) -> None:
    """Plot density, empirical CDF, and absolute exceedance probability."""
    if frame.empty:
        fig, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
        axis.axis("off")
        axis.text(
            0.5,
            0.5,
            "No exact observed comparison points are available.",
            ha="center",
            va="center",
            fontsize=13,
        )
        fig.suptitle(title, fontsize=13)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.stem + ".tmp" + destination.suffix)
        fig.savefig(temporary, dpi=160, bbox_inches="tight")
        plt.close(fig)
        temporary.replace(destination)
        return
    ordered = frame.sort_values("bubble_pct")
    magnitude = frame.assign(abs_bubble_pct=frame["bubble_pct"].abs()).sort_values(
        "abs_bubble_pct"
    )
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)

    axes[0].hist(
        frame["bubble_pct"],
        bins=_histogram_bins(frame["bubble_pct"]),
        density=True,
        color="#4472C4",
        alpha=0.8,
        edgecolor="white",
    )
    axes[0].axvline(0, color="#555555", linewidth=1)
    axes[0].set(title="Distribution", xlabel="Bubble (%)", ylabel="Density")

    axes[1].step(
        ordered["bubble_pct"], ordered["empirical_cdf"], where="post", color="#2F5597"
    )
    axes[1].axvline(0, color="#999999", linewidth=1)
    axes[1].set(title="Empirical CDF", xlabel="Bubble (%)", ylabel="F(x)", ylim=(0, 1.02))

    axes[2].step(
        magnitude["abs_bubble_pct"],
        magnitude["abs_exceedance_probability"],
        where="post",
        color="#C00000",
    )
    axes[2].set(
        title="Absolute exceedance",
        xlabel="|Bubble| (%)",
        ylabel="P(|Bubble| >= |x|)",
        ylim=(0, 1.02),
    )

    fig.suptitle(f"{title} (n={len(frame):,})", fontsize=13)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.stem + ".tmp" + destination.suffix)
    fig.savefig(temporary, dpi=160, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(destination)


def plot_distribution_plotly(frame: pd.DataFrame, title: str):
    """Return an interactive three-panel Plotly distribution figure."""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    if frame.empty:
        figure = go.Figure()
        figure.add_annotation(
            text="No observed comparison points are available.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 16},
        )
        figure.update_layout(title=title, template="plotly_white", height=430)
        return figure

    ordered = frame.sort_values("bubble_pct")
    magnitude = frame.assign(abs_bubble_pct=frame["bubble_pct"].abs()).sort_values(
        "abs_bubble_pct"
    )
    ordered_colors = np.where(ordered["is_interpolated"], "#ED7D31", "#2F5597")
    magnitude_colors = np.where(magnitude["is_interpolated"], "#ED7D31", "#C00000")
    figure = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("Distribution", "Empirical CDF", "Absolute exceedance"),
        horizontal_spacing=0.09,
    )
    figure.add_trace(
        go.Histogram(
            x=frame["bubble_pct"],
            histnorm="probability density",
            marker_color="#4472C4",
            opacity=0.85,
            name="Density",
            hovertemplate="Bubble: %{x:.2f}%<br>Density: %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=ordered["bubble_pct"],
            y=ordered["empirical_cdf"],
            mode="lines+markers",
            line={"shape": "hv", "color": "#2F5597", "width": 2},
            marker={"size": 6, "color": ordered_colors},
            customdata=ordered[["point_method"]],
            name="F(x)",
            hovertemplate=(
                "Bubble: %{x:.2f}%<br>F(x): %{y:.2%}"
                "<br>Method: %{customdata[0]}<extra></extra>"
            ),
        ),
        row=1,
        col=2,
    )
    figure.add_trace(
        go.Scatter(
            x=magnitude["abs_bubble_pct"],
            y=magnitude["abs_exceedance_probability"],
            mode="lines+markers",
            line={"shape": "hv", "color": "#C00000", "width": 2},
            marker={"size": 6, "color": magnitude_colors},
            customdata=magnitude[["point_method"]],
            name="Absolute exceedance",
            hovertemplate=(
                "|Bubble|: %{x:.2f}%<br>Probability: %{y:.2%}"
                "<br>Method: %{customdata[0]}<extra></extra>"
            ),
        ),
        row=1,
        col=3,
    )
    figure.update_xaxes(title_text="Bubble (%)", zeroline=True, row=1, col=1)
    figure.update_xaxes(title_text="Bubble (%)", zeroline=True, row=1, col=2)
    figure.update_xaxes(title_text="|Bubble| (%)", row=1, col=3)
    figure.update_yaxes(title_text="Density", row=1, col=1)
    figure.update_yaxes(title_text="F(x)", range=[0, 1.02], tickformat=".0%", row=1, col=2)
    figure.update_yaxes(
        title_text="P(|Bubble| >= |x|)", range=[0, 1.02], tickformat=".0%", row=1, col=3
    )
    figure.update_layout(
        title=f"{title} (n={len(frame):,})",
        template="plotly_white",
        height=480,
        showlegend=False,
        bargap=0.04,
        hovermode="closest",
        margin={"l": 60, "r": 30, "t": 85, "b": 60},
    )
    if frame["is_interpolated"].any():
        figure.add_annotation(
            text="Orange markers: interpolated physical ratio",
            x=1,
            y=1.14,
            xref="paper",
            yref="paper",
            xanchor="right",
            showarrow=False,
            font={"color": "#A64B00", "size": 12},
        )
    return figure


def build_project_distributions(
    *,
    project_dir: Path,
    commodity: str,
    specs: tuple[BubbleSeriesSpec, ...],
) -> pd.DataFrame:
    """Build the standard CSV and one analytical plot for every declared series."""
    bubble_dir = project_dir / "data" / "processed" / "bubble"
    analysis_dir = project_dir / "data" / "processed" / "analysis"
    outputs = []
    for spec in specs:
        source_path = bubble_dir / spec.source_file
        source = pd.read_csv(source_path, encoding="utf-8-sig", low_memory=False)
        output = empirical_distribution(source, commodity=commodity, spec=spec)
        outputs.append(output)
        plot_distribution(
            output,
            analysis_dir / f"{spec.series_id}_distribution.png",
            f"{commodity.title()}: {spec.comparison}",
        )

    combined = pd.concat(outputs, ignore_index=True)
    if not combined.empty:
        combined = combined.sort_values(
            ["bubble_type", "series_id", "bubble_pct", "observation_date"]
        )
    _atomic_csv(combined, bubble_dir / f"{commodity}_bubble_distribution.csv")
    return combined
