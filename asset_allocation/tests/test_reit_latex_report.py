from asset_allocation.build_reit_latex_report import latex, tabular


def test_latex_table_escapes_values_and_preserves_structure():
    result = tabular(["Fund", "Return %"], [["A&B", "+12.5%"]])
    assert r"A\&B & +12.5\%" in result
    assert result.count(r"\begin{tabular}") == 1
    assert result.count(r"\end{tabular}") == 1
    assert latex("a_b") == r"a\_b"
