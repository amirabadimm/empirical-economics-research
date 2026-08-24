"""Explicit exploratory product scopes for the steel rebar project."""

from __future__ import annotations

import re
from typing import Any

from shared.ime_data.ime_physical_collector import normalize_fa


CASH_CONTRACTS = {"\u0646\u0642\u062f\u06cc", "\u0646\u0642\u062f\u06cc (\u0645\u0686\u06cc\u0646\u06af)"}
EXCLUDED_PRODUCT_WORDS = (
    "\u0633\u0628\u062f", "\u06a9\u0644\u0627\u0641", "\u0622\u0644\u06cc\u0627\u0698", "\u06a9\u0648\u062a\u0627\u0647", "\u062a\u06cc\u0631",
    "\u0646\u0628\u0634\u06cc", "\u0646\u0627\u0648\u062f\u0627\u0646\u06cc", "\u0645\u062e\u0644\u0648\u0637", "\u0633\u0627\u062f\u0647",
    "\u0635\u0646\u0639\u062a\u06cc", "\u0634\u0627\u062e\u0647",
)
REBAR_DIAMETERS_MM = {"8", "10", "12", "14", "16", "18", "20", "22", "25", "28", "32"}
A3_12_PRODUCT = "A3 / 12 mm"


def canonical_straight_rebar_label(goods_name: Any) -> str | None:
    """Return a diameter/grade key for plainly specified straight rebar only.

    The deliberately strict screen excludes baskets, coil, alloy, short-length,
    and multi-product labels. It is an exploratory scope, not a technical
    deliverability certification.
    """
    name = normalize_fa(goods_name)
    if not name or any(word in name for word in EXCLUDED_PRODUCT_WORDS):
        return None
    grades = re.findall(r"(?i)A[1-4]", name)
    diameters = re.findall(r"(?<!\d)(?:8|10|12|14|16|18|20|22|25|28|32)(?!\d)", name)
    if len(grades) != 1 or len(diameters) != 1 or diameters[0] not in REBAR_DIAMETERS_MM:
        return None
    return f"{grades[0].upper()} / {diameters[0]} mm"


def is_a3_12_straight_rebar(goods_name: Any) -> bool:
    """Return whether a source goods label is the exploratory A3 / 12 mm scope."""
    return canonical_straight_rebar_label(goods_name) == A3_12_PRODUCT
