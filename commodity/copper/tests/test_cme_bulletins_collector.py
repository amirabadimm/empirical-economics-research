from commodity.copper.src.copper.collectors.cme_bulletins import _number, parse_bulletin


def test_parse_bulletin_rejects_non_pdf() -> None:
    try:
        parse_bulletin(b"not a pdf")
    except Exception:
        return
    raise AssertionError("invalid PDF payload was accepted")


def test_number_tolerates_cme_pdf_markers_and_merged_words() -> None:
    assert _number("6.6445B/6.5340") == 6.6445
    assert _number("UNCH----", integer=True) is None
    assert _number("1,234", integer=True) == 1234
