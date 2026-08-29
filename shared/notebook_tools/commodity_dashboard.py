"""Consistent read-only Plotly market dashboards for commodity notebooks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.ime_data.ime_physical_collector import jalali_to_gregorian


PLOTLY_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}
PAPER_COLOR = "#F3F5F8"
PLOT_COLOR = "#FFFFFF"
GRID_COLOR = "#DDE3EA"
TEXT_COLOR = "#243447"


def _style_figure(fig: go.Figure) -> None:
    """Apply the shared responsive research-dashboard presentation contract."""
    fig.update_layout(
        autosize=True,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        font={"family": "Arial, Tahoma, sans-serif", "size": 13, "color": TEXT_COLOR},
        title={"x": 0.02, "xanchor": "left", "font": {"size": 20}},
        hoverlabel={"bgcolor": "#FFFFFF", "font": {"color": TEXT_COLOR}},
        margin={"l": 80, "r": 35, "t": 90, "b": 65},
    )
    fig.update_xaxes(
        automargin=True,
        showgrid=True,
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor="#B8C2CC",
    )
    fig.update_yaxes(
        automargin=True,
        showgrid=True,
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor="#B8C2CC",
    )


def _jalali_series(values: pd.Series) -> pd.Series:
    def convert(value: object) -> pd.Timestamp:
        year, month, day = map(int, str(value).replace("-", "/").split("/")[:3])
        return pd.Timestamp(*jalali_to_gregorian(year, month, day))

    return values.map(convert)


def _numeric(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")


def load_markets(
    project_dir: Path, slug: str, physical_filename: str | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load canonical physical and certificate records without mutating raw data."""
    physical = pd.read_csv(
        project_dir / "data" / "raw" / "physical"
        / (physical_filename or f"{slug}_physical_raw.csv"),
        encoding="utf-8-sig",
        low_memory=False,
    )
    certificate = pd.read_csv(
        project_dir / "data" / "raw" / "certificate" / f"{slug}_certificate_raw.csv",
        encoding="utf-8-sig",
        low_memory=False,
    )
    _numeric(physical, ["Quantity", "Price", "TotalPrice"])
    _numeric(certificate, ["TradesVolume", "TradesValue", "TodaySettlementPrice"])
    physical["date_gregorian"] = _jalali_series(physical["date"])
    certificate["date_gregorian"] = pd.to_datetime(certificate["DT"].str[:10])
    return physical, certificate


def market_summary(physical: pd.DataFrame, certificate: pd.DataFrame) -> pd.DataFrame:
    """Return comparable source and positive-trade coverage statistics."""
    rows = [
        {
            "market": "physical",
            "source_records": len(physical),
            "positive_trade_records": int((physical["Quantity"].fillna(0) > 0).sum()),
            "trading_days": int(physical.loc[physical["Quantity"].fillna(0) > 0, "date"].nunique()),
            "first_date": physical["date"].min(),
            "last_date": physical["date"].max(),
        },
        {
            "market": "certificate",
            "source_records": len(certificate),
            "positive_trade_records": int((certificate["TradesVolume"].fillna(0) > 0).sum()),
            "trading_days": int(
                certificate.loc[certificate["TradesVolume"].fillna(0) > 0, "PersianDate"].nunique()
            ),
            "first_date": certificate["PersianDate"].min(),
            "last_date": certificate["PersianDate"].max(),
        },
    ]
    return pd.DataFrame(rows).set_index("market")


def plot_trade_activity(physical: pd.DataFrame, certificate: pd.DataFrame, title: str) -> None:
    """Plot daily physical quantity and certificate volume on separate, honest scales."""
    physical = physical.copy()
    physical["source_unit"] = physical["Unit"].fillna("<missing>").astype(str)
    physical_daily = physical.groupby(["source_unit", "date_gregorian"])["Quantity"].sum().sort_index()
    certificate_daily = certificate.groupby("date_gregorian")["TradesVolume"].sum().sort_index()
    units = list(physical_daily.index.get_level_values("source_unit").unique())
    rows = len(units) + 1
    fig = make_subplots(
        rows=rows, cols=1,
        subplot_titles=[f"Physical traded quantity — unit {unit}" for unit in units]
        + ["Certificate traded volume"],
        vertical_spacing=min(0.08, 0.25 / rows),
    )
    for row_number, unit in enumerate(units, start=1):
        series = physical_daily.loc[unit]
        fig.add_trace(
            go.Bar(
                x=series.index, y=series.values, name=f"Physical ({unit})",
                marker_color="#35618f",
                hovertemplate="Date=%{x|%Y-%m-%d}<br>Quantity=%{y:,.2f}<extra></extra>",
            ), row=row_number, col=1,
        )
        fig.update_yaxes(title_text=unit, row=row_number, col=1)
    fig.add_trace(
        go.Bar(
            x=certificate_daily.index, y=certificate_daily.values, name="Certificate",
            marker_color="#bf6b32",
            hovertemplate="Date=%{x|%Y-%m-%d}<br>Volume=%{y:,.0f}<extra></extra>",
        ), row=rows, col=1,
    )
    fig.update_yaxes(title_text="Certificate units", row=rows, col=1)
    fig.update_xaxes(title_text="Gregorian date", row=rows, col=1)
    fig.update_layout(
        title=f"{title}: physical and certificate trade activity", height=310 * rows,
        template="plotly_white", showlegend=False, hovermode="x unified",
    )
    _style_figure(fig)
    fig.show(config=PLOTLY_CONFIG)


def plot_market_prices(physical: pd.DataFrame, certificate: pd.DataFrame, title: str) -> None:
    """Plot positive-trade daily VWAPs without claiming cross-market comparability."""
    traded = physical.loc[(physical["Quantity"] > 0) & (physical["Price"] > 0)].copy()
    traded["price_basis"] = (
        traded["Currency"].fillna("<missing>").astype(str) + " / "
        + traded["Unit"].fillna("<missing>").astype(str)
    )
    physical_price = traded.groupby(["price_basis", "date_gregorian"]).apply(
        lambda rows: (rows["Price"] * rows["Quantity"]).sum() / rows["Quantity"].sum(),
        include_groups=False,
    )
    certificate_price = (
        certificate.loc[certificate["TradesVolume"] > 0]
        .set_index("date_gregorian")["TodaySettlementPrice"].sort_index()
    )
    bases = list(physical_price.index.get_level_values("price_basis").unique())
    rows = len(bases) + 1
    fig = make_subplots(
        rows=rows, cols=1,
        subplot_titles=[f"Broad physical daily VWAP — {basis}" for basis in bases]
        + ["Certificate settlement on traded days"],
        vertical_spacing=min(0.08, 0.25 / rows),
    )
    for row_number, basis in enumerate(bases, start=1):
        series = physical_price.loc[basis]
        fig.add_trace(
            go.Scatter(
                x=series.index, y=series.values, mode="lines", name=f"Physical ({basis})",
                line={"color": "#35618f", "width": 1.5},
                hovertemplate="Date=%{x|%Y-%m-%d}<br>VWAP=%{y:,.2f}<extra></extra>",
            ), row=row_number, col=1,
        )
        fig.update_yaxes(title_text=basis, row=row_number, col=1)
    fig.add_trace(
        go.Scatter(
            x=certificate_price.index, y=certificate_price.values, mode="lines",
            name="Certificate settlement", line={"color": "#bf6b32", "width": 1.5},
            hovertemplate="Date=%{x|%Y-%m-%d}<br>Settlement=%{y:,.2f}<extra></extra>",
        ), row=rows, col=1,
    )
    fig.update_yaxes(title_text="IRR / certificate unit", row=rows, col=1)
    fig.update_xaxes(title_text="Gregorian date", row=rows, col=1)
    fig.update_layout(
        title=f"{title}: physical and certificate prices (separate source bases)",
        height=310 * rows, template="plotly_white", showlegend=False, hovermode="x unified",
    )
    _style_figure(fig)
    fig.show(config=PLOTLY_CONFIG)


def goods_type_counts(physical: pd.DataFrame) -> pd.DataFrame:
    """Count every physical source record by the unmodified GoodsName label."""
    counts = physical["GoodsName"].fillna("<missing>").value_counts(dropna=False).rename("record_count")
    result = counts.rename_axis("goods_name").reset_index()
    result["share_pct"] = result["record_count"] / len(physical) * 100
    return result


def plot_goods_type_counts(physical: pd.DataFrame, title: str, top_n: int = 30) -> pd.DataFrame:
    """Plot the most frequent physical GoodsName labels and return their audit table."""
    table = goods_type_counts(physical)
    plot_table = table.head(top_n).sort_values("record_count")
    fig = go.Figure(go.Bar(
        x=plot_table["record_count"], y=plot_table["goods_name"], orientation="h",
        marker_color="#4f7f62", customdata=plot_table[["share_pct"]],
        hovertemplate="Goods=%{y}<br>Records=%{x:,}<br>Share=%{customdata[0]:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        title=f"{title}: physical goods types by source-record count",
        xaxis_title="Physical source records", yaxis_title="GoodsName",
        height=max(600, len(plot_table) * 27), template="plotly_white",
        margin={"l": 100, "r": 30, "t": 80, "b": 60},
    )
    _style_figure(fig)
    fig.show(config=PLOTLY_CONFIG)
    print(
        f"Distinct physical GoodsName labels: {len(table):,}; "
        f"records counted: {table['record_count'].sum():,}"
    )
    return table


def plot_available_bubbles(project_dir: Path, title: str) -> list[str]:
    """Plot validated processed bubble series, or show explicitly that none exists."""
    bubble_dir = project_dir / "data" / "processed" / "bubble"
    candidates = sorted(bubble_dir.glob("*.csv")) if bubble_dir.exists() else []
    plotted: list[str] = []
    fig = go.Figure()
    for path in candidates:
        frame = pd.read_csv(path, encoding="utf-8-sig")
        if "date" not in frame:
            continue
        for column in [column for column in frame if column.endswith("bubble_pct")]:
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(frame["date"]), y=frame[column], mode="lines",
                name=f"{path.stem}: {column}",
                hovertemplate="Date=%{x|%Y-%m-%d}<br>Bubble=%{y:.2f}%<extra></extra>",
            ))
            plotted.append(f"{path.name}:{column}")
    if plotted:
        fig.add_hline(y=0, line_color="black", line_width=0.8)
        fig.update_layout(
            title=f"{title}: validated processed bubble series", yaxis_title="Bubble (%)",
            xaxis_title="Gregorian date", template="plotly_white", hovermode="x unified", height=520,
        )
    else:
        fig.add_annotation(
            text="No validated processed bubble dataset exists.<br>No bubble was calculated or inferred.",
            x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font={"size": 16},
        )
        fig.update_layout(
            title=f"{title}: bubble analysis status", template="plotly_white", height=360,
            xaxis={"visible": False}, yaxis={"visible": False},
        )
        print("No validated processed bubble dataset exists. No bubble was calculated or inferred.")
    _style_figure(fig)
    fig.show(config=PLOTLY_CONFIG)
    return plotted
