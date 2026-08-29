"""Consistent read-only market dashboards for commodity notebooks."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from shared.ime_data.ime_physical_collector import jalali_to_gregorian


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
        project_dir
        / "data"
        / "raw"
        / "physical"
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
    physical_daily = (
        physical.groupby(["source_unit", "date_gregorian"])["Quantity"].sum().sort_index()
    )
    certificate_daily = (
        certificate.groupby("date_gregorian", as_index=True)["TradesVolume"].sum().sort_index()
    )
    units = list(physical_daily.index.get_level_values("source_unit").unique())
    fig, axes = plt.subplots(
        len(units) + 1, 1, figsize=(14, 3 * (len(units) + 1)), constrained_layout=True
    )
    axes = list(axes)
    for axis, unit in zip(axes[:-1], units, strict=True):
        series = physical_daily.loc[unit]
        axis.bar(series.index, series.values, width=5, color="#35618f")
        axis.set(title=f"{title}: physical traded quantity — unit {unit}", ylabel=unit)
    axes[-1].bar(certificate_daily.index, certificate_daily.values, width=1, color="#bf6b32")
    axes[-1].set(
        title="Certificate traded volume", ylabel="Certificate units", xlabel="Gregorian date"
    )
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    plt.show()


def plot_market_prices(physical: pd.DataFrame, certificate: pd.DataFrame, title: str) -> None:
    """Plot positive-trade daily VWAPs without claiming cross-market comparability."""
    traded = physical.loc[(physical["Quantity"] > 0) & (physical["Price"] > 0)].copy()
    traded["price_basis"] = (
        traded["Currency"].fillna("<missing>").astype(str)
        + " / "
        + traded["Unit"].fillna("<missing>").astype(str)
    )
    physical_price = traded.groupby(["price_basis", "date_gregorian"]).apply(
        lambda rows: (rows["Price"] * rows["Quantity"]).sum() / rows["Quantity"].sum(),
        include_groups=False,
    )
    certificate_price = (
        certificate.loc[certificate["TradesVolume"] > 0]
        .set_index("date_gregorian")["TodaySettlementPrice"]
        .sort_index()
    )
    bases = list(physical_price.index.get_level_values("price_basis").unique())
    fig, axes = plt.subplots(
        len(bases) + 1, 1, figsize=(14, 3 * (len(bases) + 1)), constrained_layout=True
    )
    axes = list(axes)
    for axis, basis in zip(axes[:-1], bases, strict=True):
        series = physical_price.loc[basis]
        axis.plot(series.index, series.values, color="#35618f", linewidth=1)
        axis.set(title=f"{title}: broad physical daily VWAP — {basis}", ylabel=basis)
    axes[-1].plot(
        certificate_price.index, certificate_price.values, color="#bf6b32", linewidth=1
    )
    axes[-1].set(
        title="Certificate settlement on traded days",
        ylabel="IRR / certificate unit",
        xlabel="Gregorian date",
    )
    for axis in axes:
        axis.grid(alpha=0.25)
    plt.show()


def goods_type_counts(physical: pd.DataFrame) -> pd.DataFrame:
    """Count every physical source record by the unmodified GoodsName label."""
    counts = (
        physical["GoodsName"].fillna("<missing>").value_counts(dropna=False).rename("record_count")
    )
    result = counts.rename_axis("goods_name").reset_index()
    result["share_pct"] = result["record_count"] / len(physical) * 100
    return result


def plot_goods_type_counts(physical: pd.DataFrame, title: str, top_n: int = 30) -> pd.DataFrame:
    """Plot the most frequent physical GoodsName labels and return their audit table."""
    table = goods_type_counts(physical)
    plot_table = table.head(top_n).sort_values("record_count")
    fig, axis = plt.subplots(figsize=(12, max(6, len(plot_table) * 0.32)))
    axis.barh(plot_table["goods_name"], plot_table["record_count"], color="#4f7f62")
    axis.set(
        title=f"{title}: physical goods types by source-record count",
        xlabel="Physical source records",
        ylabel="GoodsName",
    )
    axis.grid(axis="x", alpha=0.25)
    plt.tight_layout()
    plt.show()
    print(
        f"Distinct physical GoodsName labels: {len(table):,}; records counted: {table['record_count'].sum():,}"
    )
    return table


def plot_available_bubbles(project_dir: Path, title: str) -> list[str]:
    """Plot validated processed bubble series, or state explicitly that none exists."""
    bubble_dir = project_dir / "data" / "processed" / "bubble"
    candidates = sorted(bubble_dir.glob("*.csv")) if bubble_dir.exists() else []
    plotted: list[str] = []
    fig, axis = plt.subplots(figsize=(14, 5))
    for path in candidates:
        frame = pd.read_csv(path, encoding="utf-8-sig")
        if "date" not in frame:
            continue
        bubble_columns = [column for column in frame if column.endswith("bubble_pct")]
        for column in bubble_columns:
            axis.plot(
                pd.to_datetime(frame["date"]),
                frame[column],
                linewidth=1,
                label=f"{path.stem}: {column}",
            )
            plotted.append(f"{path.name}:{column}")
    if plotted:
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set(
            title=f"{title}: validated processed bubble series",
            ylabel="Bubble (%)",
            xlabel="Gregorian date",
        )
        axis.legend(fontsize=8)
        axis.grid(alpha=0.25)
        plt.tight_layout()
        plt.show()
    else:
        plt.close(fig)
        print(
            "No validated processed bubble dataset exists. No bubble was calculated or inferred in this notebook."
        )
    return plotted
