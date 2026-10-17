"""Derive initial public subscription proceeds from immutable TSETMC trade snapshots.

The session windows come from TSETMC supervisor subscription notices. Sponsor
attribution is kept separate from a legal founder list in the source notes.
"""
from __future__ import annotations

import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame
from asset_allocation.build_reit_assembly_reinvestment import FUNDS, ROOT
from asset_allocation.build_reit_data_handoff import jalali, trading_value_archive

DATA = ROOT / "data/processed/analysis"
NOTICE = "https://cdn.tsetmc.com/api/Msg/GetMsgByInsCode/"

# First and last public subscription sessions, verified against exchange notices.
WINDOWS = {
    "71945594172117613": ("2022-10-18", "2022-10-18"),
    "67717913151786055": ("2023-08-01", "2023-08-05"),
    "70814244102598215": ("2023-12-18", "2023-12-19"),
    "37118058361762279": ("2024-04-23", "2024-04-24"),
    "45292762906823004": ("2024-09-28", "2024-10-01"),
    "34322849244939912": ("2025-05-12", "2025-05-12"),
    "71595553356620707": ("2026-02-22", "2026-02-24"),
    "41480981133648877": ("2026-05-13", "2026-05-13"),
}

# Named founding entities from notices and, for Danik and Kashaneh, the signed
# founding statute tables. A contracted party without a founder role is omitted.
SPONSORS = {
    "71945594172117613": "صندوق بازنشستگی کشوری؛ گروه مدیریت ارزش سرمایه صندوق بازنشستگی کشوری؛ عمران و ساختمان بازنشستگی کشوری",
    "67717913151786055": "گروه مالی دانایان؛ مدیریت سرمایه و ساخت نیک‌رای؛ سرمایه‌گذاری دانایان؛ صندوق سرمایه‌گذاری اختصاصی بازارگردانی دانایان",
    "70814244102598215": "بانک شهر؛ شرکت مسکن و عمران تجارت آتیه کیش؛ مشاور سرمایه‌گذاری امین نیکان آفاق",
    "37118058361762279": "تأمین سرمایه بانک مسکن؛ گروه خدمات بازار سرمایه آرمان آتی؛ سرمایه‌گذاری تأمین آتیه مسکن",
    "45292762906823004": "سبدگردان آگاه؛ مشاور سرمایه‌گذاری آوای آگاه؛ کارگزاری آگاه",
    "34322849244939912": "تأمین سرمایه دماوند؛ سرمایه‌گذاری اعتضاد غدیر؛ کانون نهادهای سرمایه‌گذاری ایران؛ تأمین سرمایه بانک مسکن",
    "71595553356620707": "سبدگردان کاریزما؛ گروه خدمات بازار سرمایه کاریزما؛ سرمایه‌گذاری عمرانی پرداس",
    "41480981133648877": "بانک دی؛ سرمایه‌گذاری گروه مالی و اقتصادی دی؛ توسعه دیدار ایرانیان",
}
SPONSOR_SOURCES = {
    "71945594172117613": "https://didgahnews.ir/پذیره‌نویسی-اولین-صندوق-املاک-در-فراب/",
    "67717913151786055": "https://nikrayreits.ir/Download/DownloadPDFByAttachmentId?attachmentId=547",
    "70814244102598215": "https://tejaratgardan.ir/پذیره-نویسی-صندوق-امین-شهر-یکم-آغاز-ش/",
    "37118058361762279": "https://eghtesadjournal.com/bank-insurance-budget/99835/",
    "45292762906823004": NOTICE + "45292762906823004",
    "34322849244939912": "https://kashane.pgibc.ir/Download/DownloadPDFByAttachmentId?attachmentId=523",
    "71595553356620707": NOTICE + "71595553356620707",
    "41480981133648877": NOTICE + "41480981133648877",
}


def build() -> pd.DataFrame:
    daily = pd.read_csv(DATA / "reit_daily_series.csv", dtype={"ins_code": str})
    archive = trading_value_archive()
    if set(WINDOWS) != set(FUNDS) or set(SPONSORS) != set(FUNDS):
        raise ValueError("Subscription evidence roster mismatch")
    rows = []
    for code, name in FUNDS.items():
        start, end = WINDOWS[code]
        notices = sorted((ROOT / "data/raw/real_estate_funds/subscription_notice_snapshots").glob(f"{code}_*.json"))
        if not notices:
            raise ValueError(f"Missing immutable TSETMC notice snapshot: {code}")
        statutes = sorted((ROOT / "data/raw/real_estate_funds/founder_statute_snapshots").glob(f"{code}_*.pdf"))
        if code in {"67717913151786055", "34322849244939912"} and not statutes:
            raise ValueError(f"Missing immutable signed statute: {code}")
        window = daily.loc[(daily.ins_code == code) & daily.date_gregorian.between(start, end) & daily.has_trade]
        if window.empty or window.iloc[0].date_gregorian != start:
            raise ValueError(f"Missing first subscription trade: {code}")
        if not window.raw_close_irr.eq(10000).all():
            raise ValueError(f"Subscription price is not 10,000 IRR: {code}")
        for row in window.itertuples():
            evidence = archive[(code, row.date_gregorian)]
            if int(row.trading_value_irr_qTotCap) != evidence["trading_value_irr"]:
                raise ValueError(f"Subscription value differs from raw snapshot: {code}")
            if int(row.trading_value_irr_qTotCap) != int(row.trade_volume_units) * 10000:
                raise ValueError(f"Subscription volume/value inconsistency: {code}")
        units = int(window.trade_volume_units.sum())
        rows.append({
            "fund": name, "ins_code": code,
            "subscription_date_gregorian": start,
            "subscription_date_jalali": jalali(start),
            "subscription_last_session_gregorian": end,
            "subscription_session_count": len(window),
            "initial_public_subscription_units": units,
            "subscription_proceeds_billion_toman": units / 1_000_000,
            "founder_or_sponsor": SPONSORS[code],
            "founder_status": "named_founders_in_signed_statute" if code in {"67717913151786055", "34322849244939912"} else "named_founders_in_public_notice",
            "subscription_notice_url": NOTICE + code,
            "subscription_notice_snapshot_path": notices[-1].relative_to(ROOT).as_posix(),
            "founder_source_url": SPONSOR_SOURCES[code],
            "founder_statute_snapshot_path": statutes[-1].relative_to(ROOT).as_posix() if statutes else None,
            "founder_statute_pdf_page": 37 if code == "67717913151786055" else 34 if code == "34322849244939912" else None,
            "proceeds_source": "TSETMC_immutable_qTotCap_subscription_sessions_10000_IRR_per_unit",
        })
    result = pd.DataFrame(rows)
    atomic_frame(DATA / "reit_subscription_facts.csv", result)
    return result


if __name__ == "__main__":
    print(build().to_string(index=False))
