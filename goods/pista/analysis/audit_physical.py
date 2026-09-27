"""Audit the company-provided weekly prices without changing the source workbook."""

from __future__ import annotations

import argparse
import os
import tempfile
from bisect import bisect_left
from datetime import date
from pathlib import Path

import jdatetime
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data/raw/physical/Pistachio_Weekly_Prices.xlsx"
INTERIM = PROJECT_ROOT / "data/interim"
DATE_COLUMN = "Date (Jalali)"
PRODUCTS = ("Khandan", "Dahan-Bast")
WIDE_RANGE_THRESHOLD = 0.25
WEEKLY_CHANGE_THRESHOLD = 0.25
ISOLATED_DEVIATION_THRESHOLD = 0.15
SOURCE_COLUMNS = [DATE_COLUMN] + [
    f"{product} {measure} Price"
    for product in PRODUCTS
    for measure in ("Min", "Max", "Average")
]
AUDIT_COLUMNS = [
    "jalali_date", "product", "original_min", "original_max", "original_average",
    "previous_valid_observation", "next_valid_observation",
    "percentage_deviation_from_local_median", "min_max_range_percentage",
    "reason_for_flagging", "proposed_correction", "confidence_level", "action",
]


def gregorian_date(value: str) -> date | None:
    try:
        year, month, day = map(int, value.split("/"))
        return jdatetime.date(year, month, day).togregorian()
    except (TypeError, ValueError):
        return None


def load_source(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, engine="openpyxl", dtype={DATE_COLUMN: str})
    if list(frame.columns) != SOURCE_COLUMNS:
        raise ValueError(f"Unexpected workbook columns: {list(frame.columns)!r}")
    frame[DATE_COLUMN] = frame[DATE_COLUMN].str.strip()
    for column in SOURCE_COLUMNS[1:]:
        raw = frame[column]
        numeric = pd.to_numeric(raw, errors="coerce")
        if (raw.notna() & numeric.isna()).any():
            raise ValueError(f"Non-numeric source values in {column}")
        frame[column] = numeric
    return frame


def observation(frame: pd.DataFrame, index: int | None, product: str) -> str:
    if index is None:
        return ""
    row = frame.iloc[index]
    return (
        f"{row[DATE_COLUMN]}: min={row[f'{product} Min Price']:g}, "
        f"max={row[f'{product} Max Price']:g}, "
        f"average={row[f'{product} Average Price']:g}"
    )


def missing_blocks(mask: pd.Series) -> list[tuple[int, int]]:
    blocks = []
    start = None
    for index, missing in enumerate(mask):
        if missing and start is None:
            start = index
        elif not missing and start is not None:
            blocks.append((start, index - 1))
            start = None
    if start is not None:
        blocks.append((start, len(mask) - 1))
    return blocks


def neighboring_indices(indices: list[int], index: int) -> tuple[int | None, int | None]:
    position = bisect_left(indices, index)
    previous = indices[position - 1] if position else None
    if position < len(indices) and indices[position] == index:
        position += 1
    following = indices[position] if position < len(indices) else None
    return previous, following


def audit(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned = frame.copy(deep=True)
    dates = [gregorian_date(value) for value in frame[DATE_COLUMN]]
    duplicates = frame[DATE_COLUMN].duplicated(keep=False)
    flags: dict[tuple[int, str], list[str]] = {}
    manual: set[tuple[int, str]] = set()
    notes: dict[tuple[int, str], str] = {}
    neighbors: dict[str, list[int]] = {}

    def flag(index: int, product: str, reason: str, review: bool = False) -> None:
        key = index, product
        flags.setdefault(key, []).append(reason)
        if review:
            manual.add(key)

    for product in PRODUCTS:
        minimum, maximum, average = (f"{product} {measure} Price" for measure in ("Min", "Max", "Average"))
        lo, hi, avg = (frame[column] for column in (minimum, maximum, average))
        complete = lo.notna() & hi.notna()
        valid = complete & (lo > 0) & (hi > 0) & (lo <= hi)
        midpoint = (lo + hi) / 2
        valid_indices = [i for i, ok in enumerate(valid) if ok]
        neighbors[product] = valid_indices

        for start, end in missing_blocks(lo.isna() & hi.isna() & avg.isna()):
            count = end - start + 1
            reason = (
                f"missing_block: {count} source row(s), "
                f"{frame.at[start, DATE_COLUMN]} to {frame.at[end, DATE_COLUMN]}"
            )
            flag(start, product, reason)
            if end + 1 < len(frame) and count >= 4:
                flag(end + 1, product, f"first observation after {count}-row missing block", review=True)

        for i in range(len(frame)):
            key = i, product
            previous, following = neighboring_indices(valid_indices, i)

            if dates[i] is None:
                flag(i, product, "invalid Jalali calendar date", review=True)
            if duplicates.iloc[i]:
                flag(i, product, "duplicate Jalali date", review=True)
            if i and dates[i] is not None and dates[i - 1] is not None and dates[i] < dates[i - 1]:
                flag(i, product, "dates out of order", review=True)
            if i and dates[i] is not None and dates[i - 1] is not None and (dates[i] - dates[i - 1]).days > 21:
                flag(i, product, f"calendar gap of {(dates[i] - dates[i - 1]).days} days")

            if pd.isna(lo.iloc[i]) != pd.isna(hi.iloc[i]):
                flag(i, product, "partial Min/Max observation", review=True)
            if not complete.iloc[i]:
                if avg.notna().iloc[i]:
                    flag(i, product, "Average present without both Min and Max", review=True)
                continue
            if lo.iloc[i] <= 0 or hi.iloc[i] <= 0:
                flag(i, product, "zero or negative price", review=True)
            if lo.iloc[i] > hi.iloc[i]:
                flag(i, product, "Min greater than Max", review=True)
            if not valid.iloc[i]:
                continue

            if pd.isna(avg.iloc[i]) or abs(avg.iloc[i] - midpoint.iloc[i]) > 1e-7:
                flag(i, product, "Average missing or differs from (Min + Max) / 2")
                notes[key] = f"Average {avg.iloc[i]:g} -> {midpoint.iloc[i]:g}; Min and Max unchanged"

            range_pct = (hi.iloc[i] - lo.iloc[i]) / midpoint.iloc[i]
            if range_pct >= WIDE_RANGE_THRESHOLD:
                flag(i, product, f"wide Min-Max range ({range_pct:.1%} of midpoint)", review=True)

            if any(value % 50 for value in (lo.iloc[i], hi.iloc[i])):
                flag(i, product, "price precision differs from the source's usual 50-unit grid", review=True)

            if (
                previous is not None
                and dates[i] is not None
                and dates[previous] is not None
                and (dates[i] - dates[previous]).days <= 21
            ):
                change = midpoint.iloc[i] / midpoint.iloc[previous] - 1
                if abs(change) >= WEEKLY_CHANGE_THRESHOLD:
                    flag(i, product, f"large change from previous observation ({change:+.1%})")

            if previous is not None and following is not None:
                neighbor_gap = (
                    (dates[following] - dates[previous]).days
                    if dates[following] is not None and dates[previous] is not None
                    else 9999
                )
                local = (midpoint.iloc[previous] + midpoint.iloc[following]) / 2
                deviation = midpoint.iloc[i] / local - 1
                neighbor_difference = abs(midpoint.iloc[following] / midpoint.iloc[previous] - 1)
                if (
                    neighbor_gap <= 35
                    and abs(deviation) >= ISOLATED_DEVIATION_THRESHOLD
                    and neighbor_difference <= 0.25
                ):
                    flag(
                        i, product,
                        f"isolated local deviation ({deviation:+.1%}); "
                        f"neighbors differ {neighbor_difference:.1%}",
                        review=True,
                    )
                if range_pct >= WIDE_RANGE_THRESHOLD:
                    candidates = [
                        ("Min x10", lo.iloc[i] * 10, hi.iloc[i]),
                        ("Max /10", lo.iloc[i], hi.iloc[i] / 10),
                    ]
                    plausible = [
                        label for label, a, b in candidates
                        if 0 < a <= b and abs((a + b) / (2 * local) - 1) <= 0.15
                    ]
                    if not plausible:
                        flag(
                            i, product,
                            "simple tenfold endpoint changes do not yield a valid, locally supported range",
                            review=True,
                        )
                    elif len(plausible) > 1:
                        flag(i, product, "multiple tenfold endpoint changes appear plausible", review=True)
                    else:
                        flag(
                            i, product,
                            f"possible {plausible[0]} entry error; source confirmation required",
                            review=True,
                        )

    audit_rows = []
    for (i, product), reasons in sorted(flags.items()):
        lo, hi, avg = (frame.at[i, f"{product} {measure} Price"] for measure in ("Min", "Max", "Average"))
        previous, following = neighboring_indices(neighbors[product], i)
        local = None
        if previous is not None and following is not None:
            previous_mid = (
                frame.at[previous, f"{product} Min Price"]
                + frame.at[previous, f"{product} Max Price"]
            ) / 2
            next_mid = (
                frame.at[following, f"{product} Min Price"]
                + frame.at[following, f"{product} Max Price"]
            ) / 2
            local = (previous_mid + next_mid) / 2
        midpoint = (lo + hi) / 2 if pd.notna(lo) and pd.notna(hi) else None
        deviation = 100 * (midpoint / local - 1) if midpoint is not None and local else None
        range_pct = 100 * (hi - lo) / midpoint if midpoint and midpoint > 0 else None
        corrected = (i, product) in notes
        action = "manual_review" if (i, product) in manual else "correct" if corrected else "keep"
        if corrected:
            cleaned.at[i, f"{product} Average Price"] = (lo + hi) / 2
        audit_rows.append({
            "jalali_date": frame.at[i, DATE_COLUMN], "product": product,
            "original_min": lo, "original_max": hi, "original_average": avg,
            "previous_valid_observation": observation(frame, previous, product),
            "next_valid_observation": observation(frame, following, product),
            "percentage_deviation_from_local_median": deviation,
            "min_max_range_percentage": range_pct,
            "reason_for_flagging": "; ".join(dict.fromkeys(reasons)),
            "proposed_correction": notes.get((i, product), ""),
            "confidence_level": "high" if corrected else "low" if (i, product) in manual else "medium",
            "action": action,
        })

    audit_frame = pd.DataFrame(audit_rows, columns=AUDIT_COLUMNS)
    actions = {(i, p): row["action"] for (i, p), row in zip(sorted(flags), audit_rows)}
    for product, column in (("Khandan", "khandan_flag"), ("Dahan-Bast", "dahan_bast_flag")):
        cleaned[column] = [actions.get((i, product), "ok") for i in range(len(frame))]
    cleaned["quality_flag"] = [
        "manual_review" if "manual_review" in pair
        else "corrected" if "correct" in pair
        else "flagged_kept" if "keep" in pair
        else "ok"
        for pair in zip(cleaned["khandan_flag"], cleaned["dahan_bast_flag"])
    ]
    cleaned["correction_applied"] = [any((i, product) in notes for product in PRODUCTS) for i in range(len(frame))]
    cleaned["correction_note"] = [
        "; ".join(notes[i, product] for product in PRODUCTS if (i, product) in notes)
        for i in range(len(frame))
    ]
    validate(frame, cleaned, audit_frame)
    return cleaned, audit_frame


def validate(original: pd.DataFrame, cleaned: pd.DataFrame, audit_frame: pd.DataFrame) -> None:
    if len(cleaned) != len(original) or not cleaned[DATE_COLUMN].equals(original[DATE_COLUMN]):
        raise AssertionError("Row count or date sequence changed")
    if cleaned[DATE_COLUMN].duplicated().sum() != original[DATE_COLUMN].duplicated().sum():
        raise AssertionError("Duplicate dates were introduced")
    for product in PRODUCTS:
        lo, hi, avg = (f"{product} {measure} Price" for measure in ("Min", "Max", "Average"))
        if (cleaned[lo].notna() & cleaned[hi].notna() & (cleaned[lo] > cleaned[hi])).any():
            raise AssertionError(f"Invalid Min-Max order in cleaned {product}")
        complete = cleaned[lo].notna() & cleaned[hi].notna()
        if cleaned.loc[complete, avg].isna().any():
            raise AssertionError(f"Missing derived Average in cleaned {product}")
        average_error = (
            cleaned.loc[complete, avg]
            - (cleaned.loc[complete, lo] + cleaned.loc[complete, hi]) / 2
        ).abs()
        if (average_error > 1e-7).any():
            raise AssertionError(f"Average mismatch in cleaned {product}")
        for column in (lo, hi, avg):
            filled = original[column].isna() & cleaned[column].notna()
            if column == avg:
                filled &= ~cleaned["correction_applied"]
            if filled.any():
                raise AssertionError(f"Missing source values were filled in {column}")
            if (original[column].gt(0) & cleaned[column].eq(0)).any():
                raise AssertionError(f"Positive source prices became zero in {column}")
    corrections = audit_frame[audit_frame["proposed_correction"].ne("")]
    if not corrections["confidence_level"].eq("high").all():
        raise AssertionError("A non-high-confidence correction was applied")


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as handle:
            frame.to_csv(handle, index=False, float_format="%.10g")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, default=INTERIM)
    args = parser.parse_args()
    source = load_source(args.source)
    cleaned, audit_frame = audit(source)
    write_csv_atomic(cleaned, args.output_dir / "pistachio_physical_cleaned.csv")
    write_csv_atomic(audit_frame, args.output_dir / "pistachio_physical_audit.csv")
    counts = audit_frame["action"].value_counts()
    print(f"Total rows: {len(source)}")
    print(f"Flagged product observations: {len(audit_frame)}")
    corrected = audit_frame[audit_frame["proposed_correction"].ne("")]
    print(f"Automatically corrected: {len(corrected)}")
    print(f"Flagged and retained unchanged: {counts.get('keep', 0)}")
    print(f"Requiring manual review: {counts.get('manual_review', 0)}")
    for row in corrected.itertuples(index=False):
        print(
            f"Corrected {row.jalali_date} {row.product}: "
            f"old=({row.original_min:g}, {row.original_max:g}, {row.original_average:g}); "
            f"{row.proposed_correction}"
        )


if __name__ == "__main__":
    main()
