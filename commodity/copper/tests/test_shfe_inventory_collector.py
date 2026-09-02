from commodity.copper.src.copper.collectors.shfe_inventory import english


def test_english_bilingual_label() -> None:
    assert english("\u603b\u8ba1$$Total") == "Total"
