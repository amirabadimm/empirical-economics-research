"""Build reproducible figures for the pellet LaTeX report.

This script is read-only with respect to canonical raw data. It writes report
figures only under reports/figures.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPORT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = REPORT_DIR.parent
PHYSICAL_CSV = PROJECT_DIR / "data/raw/physical/pellet_physical_raw.csv"
CERTIFICATE_CSV = PROJECT_DIR / "data/raw/certificate/pellet_certificate_raw.csv"
FIGURE_DIR = REPORT_DIR / "figures"
CERTIFICATE_START = "1404/07/28"

SELECTED = {
    "GOLG-PELL-00": "Gol Gohar",
    "GHZ-PELL-00": "Gohar Zamin",
}
SCREENED = {
    "GOLG-PELL-00": "Gol Gohar",
    "GHZ-PELL-00": "Gohar Zamin",
    "CHMI-PELL-00": "Chadormalu",
    "SSMI-PELL-00": "Sangan Khorasan",
}


def weighted_price(group: pd.DataFrame) -> float:
    return np.average(group["Price"], weights=group["Quantity"])


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    physical = pd.read_csv(PHYSICAL_CSV, encoding="utf-8-sig", low_memory=False)
    certificate = pd.read_csv(
        CERTIFICATE_CSV, encoding="utf-8-sig", low_memory=False
    )
    physical_numeric = [
        "Price", "Quantity", "ArzeBasePrice", "arze", "taghaza"
    ]
    certificate_numeric = [
        "TradesVolume", "TodaySettlementPrice", "LastSettlementPrice",
        "MinPrice", "MaxPrice",
    ]
    for column in physical_numeric:
        physical[column] = pd.to_numeric(physical[column], errors="coerce")
    for column in certificate_numeric:
        certificate[column] = pd.to_numeric(certificate[column], errors="coerce")
    return physical, certificate


def build_benchmark(
    physical: pd.DataFrame, certificate: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    strict_cash = physical.loc[
        physical["ContractType"].isin(["نقدی", "نقدی (مچینگ)"])
        & physical["Tasvieh"].eq("نقدی")
        & physical["Price"].gt(0)
        & physical["Quantity"].gt(0)
        & physical["Symbol"].isin(SELECTED)
    ].copy()

    daily = (
        strict_cash.groupby(["date", "Symbol"], sort=True)
        .apply(weighted_price, include_groups=False)
        .rename("price")
        .reset_index()
    )
    wide = daily.pivot(index="date", columns="Symbol", values="price")
    for symbol in SELECTED:
        if symbol not in wide:
            wide[symbol] = np.nan
    wide = wide.rename(columns={
        "GOLG-PELL-00": "gol_gohar_price",
        "GHZ-PELL-00": "gohar_zamin_price",
    })
    wide["physical_company_count"] = wide[
        ["gol_gohar_price", "gohar_zamin_price"]
    ].notna().sum(axis=1)
    wide["physical_benchmark"] = wide[
        ["gol_gohar_price", "gohar_zamin_price"]
    ].mean(axis=1, skipna=True)
    wide = wide.reset_index().rename(columns={"date": "PersianDate"})

    traded_certificate = certificate.loc[
        certificate["TradesVolume"].gt(0)
        & certificate["TodaySettlementPrice"].gt(0),
        [
            "PersianDate", "TradesVolume", "TodaySettlementPrice",
            "LastSettlementPrice", "MinPrice", "MaxPrice",
        ],
    ]
    bubble = (
        wide.merge(
            traded_certificate, on="PersianDate", how="inner",
            validate="one_to_one"
        )
        .sort_values("PersianDate")
        .reset_index(drop=True)
    )
    bubble["bubble_pct"] = 100 * (
        bubble["TodaySettlementPrice"] / bubble["physical_benchmark"] - 1
    )
    return daily, bubble


def save_market_share(physical: pd.DataFrame) -> None:
    market = physical.loc[
        physical["date"].ge(CERTIFICATE_START)
        & physical["Price"].gt(0)
        & physical["Quantity"].gt(0)
    ]
    total = market["Quantity"].sum()
    shares = (
        market.loc[market["Symbol"].isin(SCREENED)]
        .groupby("Symbol")["Quantity"].sum()
        .reindex(SCREENED)
        .div(total).mul(100)
    )
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bars = ax.bar(
        [SCREENED[s] for s in shares.index],
        shares.values,
        color=["#1f4e79", "#4f81bd", "#a5a5a5", "#c9c9c9"],
    )
    ax.bar_label(bars, labels=[f"{v:.2f}%" for v in shares], padding=3)
    ax.set_ylabel("Share of all positive physical volume (%)")
    ax.set_title("Producer representation since certificate launch")
    ax.set_ylim(0, max(shares) * 1.22)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "producer_market_share.png", dpi=220)
    plt.close(fig)


def save_pair_prices(daily: pd.DataFrame) -> None:
    wide = daily.pivot(index="date", columns="Symbol", values="price").sort_index()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    for symbol, label in SELECTED.items():
        if symbol in wide:
            ax.plot(
                wide.index, wide[symbol], marker="o", markersize=3.5,
                linewidth=1.4, label=label
            )
    ax.set_title("Strict-cash physical prices of selected producers")
    ax.set_xlabel("Jalali date")
    ax.set_ylabel("IRR per kg")
    ax.legend(frameon=False)
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "selected_physical_prices.png", dpi=220)
    plt.close(fig)


def save_bubble(bubble: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    colors = np.where(bubble["bubble_pct"].ge(0), "#2e8b57", "#b04a5a")
    ax.bar(bubble["PersianDate"], bubble["bubble_pct"], color=colors)
    ax.axhline(0, color="black", linewidth=0.9)
    ax.set_title("Certificate premium/discount vs. exact-date physical benchmark")
    ax.set_xlabel("Jalali date")
    ax.set_ylabel("Premium / discount (%)")
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "certificate_bubble.png", dpi=220)
    plt.close(fig)


def save_case_study(physical: pd.DataFrame, certificate: pd.DataFrame) -> None:
    cert = certificate.loc[
        certificate["PersianDate"].between("1404/10/10", "1404/10/24")
        & certificate["TradesVolume"].gt(0)
    ].sort_values("PersianDate")
    day = physical.loc[
        physical["date"].eq("1404/10/21")
        & physical["Symbol"].isin(SELECTED)
        & physical["Quantity"].gt(0)
        & physical["Price"].gt(0)
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.5))
    axes[0].plot(
        cert["PersianDate"], cert["TodaySettlementPrice"],
        color="#1f4e79", marker="o", linewidth=2
    )
    axes[0].set_title("Certificate repricing before 1404/10/21")
    axes[0].set_ylabel("Settlement price (IRR/kg)")
    axes[0].tick_params(axis="x", rotation=55, labelsize=7)
    axes[0].grid(axis="y", alpha=0.25)

    labels = ["Gol cash", "Certificate", "Gol forward/mixed", "GHZ cash/mixed"]
    values = [
        float(day.loc[
            day["Symbol"].eq("GOLG-PELL-00")
            & day["ContractType"].eq("نقدی")
            & day["Tasvieh"].eq("نقدی"), "Price"
        ].iloc[0]),
        float(cert.loc[
            cert["PersianDate"].eq("1404/10/21"), "TodaySettlementPrice"
        ].iloc[0]),
        float(day.loc[
            day["Symbol"].eq("GOLG-PELL-00")
            & day["ContractType"].eq("سلف"), "Price"
        ].iloc[0]),
        float(day.loc[
            day["Symbol"].eq("GHZ-PELL-00"), "Price"
        ].iloc[0]),
    ]
    bars = axes[1].bar(labels, values, color=["#4f81bd", "#2e8b57", "#c98b3c", "#b04a5a"])
    axes[1].bar_label(bars, labels=[f"{v:,.0f}" for v in values], padding=3)
    axes[1].set_title("Cross-section on 1404/10/21")
    axes[1].set_ylabel("IRR per kg")
    axes[1].tick_params(axis="x", rotation=30, labelsize=8)
    axes[1].set_ylim(0, max(values) * 1.18)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "positive_bubble_case.png", dpi=220)
    plt.close(fig)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    physical, certificate = load_data()
    daily, bubble = build_benchmark(physical, certificate)
    if len(bubble) != 22:
        raise ValueError(f"Expected 22 exact-date observations, got {len(bubble)}")
    if int(bubble["bubble_pct"].gt(0).sum()) != 1:
        raise ValueError("Expected exactly one positive bubble observation")
    save_market_share(physical)
    save_pair_prices(daily)
    save_bubble(bubble)
    save_case_study(physical, certificate)
    print(
        f"Built 4 figures; bubble observations={len(bubble)}, "
        f"single-producer={(bubble.physical_company_count == 1).sum()}, "
        f"two-producer={(bubble.physical_company_count == 2).sum()}"
    )


if __name__ == "__main__":
    main()
