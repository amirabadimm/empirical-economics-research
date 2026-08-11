"""Build Jalali/Excel-ready certificate and physical-market timeline files."""

from pathlib import Path

import jdatetime
import pandas as pd


def jalali(value: pd.Timestamp) -> str:
    return jdatetime.date.fromgregorian(date=value.date()).strftime("%Y/%m/%d")


def excel_serial(value: pd.Timestamp) -> int:
    return (value - pd.Timestamp("1899-12-30")).days


def main() -> None:
    project = Path(__file__).resolve().parents[3]
    raw = pd.read_csv(project / "data/raw/certificate/copper_certificate_raw.csv")
    physical = pd.read_csv(project / "data/processed/nci_copper_cash_daily.csv")

    certificate_dates = set(
        pd.to_datetime(raw.loc[pd.to_numeric(raw["TradesVolume"]) > 0, "DT"]).dt.normalize()
    )
    physical_dates_all = set(pd.to_datetime(physical["physical_trade_date_gregorian"]).dt.normalize())
    start, end = min(certificate_dates), max(certificate_dates)
    physical_dates = {value for value in physical_dates_all if start <= value <= end}
    overlap = certificate_dates & physical_dates

    calendar = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    calendar["date_jalali"] = calendar["date"].map(jalali)
    calendar["date_excel_serial"] = calendar["date"].map(excel_serial)
    calendar["certificate_trade"] = calendar["date"].isin(certificate_dates).astype(int)
    calendar["physical_trade"] = calendar["date"].isin(physical_dates).astype(int)
    calendar["exact_overlap"] = calendar["date"].isin(overlap).astype(int)
    calendar["certificate_lane"] = calendar["certificate_trade"].replace({0: pd.NA})
    calendar["physical_lane"] = calendar["physical_trade"].replace({0: pd.NA}) * 0
    daily = calendar[[
        "date_jalali", "date_excel_serial", "certificate_trade", "physical_trade",
        "exact_overlap", "certificate_lane", "physical_lane",
    ]]

    event_rows = []
    for value in sorted(certificate_dates):
        event_rows.append((jalali(value), excel_serial(value), "Certificate", 1, int(value in overlap)))
    for value in sorted(physical_dates):
        event_rows.append((jalali(value), excel_serial(value), "Physical", 0, int(value in overlap)))
    events = pd.DataFrame(
        event_rows, columns=["date_jalali", "date_excel_serial", "market", "lane", "exact_overlap"]
    ).sort_values(["date_excel_serial", "lane"], ascending=[True, False])

    destination = project / "data/processed"
    daily.to_csv(destination / "presentation_timeline_daily.csv", index=False, encoding="utf-8-sig")
    events.to_csv(destination / "presentation_timeline_events.csv", index=False, encoding="utf-8-sig")
    print(f"Daily rows: {len(daily)}; events: {len(events)}; overlaps: {len(overlap)}")


if __name__ == "__main__":
    main()
