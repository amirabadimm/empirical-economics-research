from commodity.copper.src.copper.collectors.cme_bulletins import parse_bulletin


def test_parse_bulletin_rejects_non_pdf() -> None:
    try:
        parse_bulletin(b"not a pdf")
    except Exception:
        return
    raise AssertionError("invalid PDF payload was accepted")
