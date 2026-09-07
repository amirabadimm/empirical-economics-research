from commodity.copper.src.copper.collectors.shfe_inventory import CATEGORY_NAMES, english


def test_english_bilingual_label() -> None:
    assert english("\u603b\u8ba1$$Total") == "Total"


def test_html_total_category_mapping() -> None:
    assert CATEGORY_NAMES["\u4fdd\u7a0e\u5546\u54c1\u603b\u8ba1"] == "Total (Bonded)"
    assert CATEGORY_NAMES["\u5b8c\u7a0e\u5546\u54c1\u603b\u8ba1"] == "Total (Tax included)"
