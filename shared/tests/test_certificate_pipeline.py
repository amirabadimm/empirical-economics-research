import pytest

from shared.certificate_pipeline import refresh


def test_all_plans_have_existing_scripts_and_no_global_research():
    for name in refresh.PROJECTS:
        offline = refresh.plan(name)
        online = refresh.plan(name, collect=True)
        assert len(online) > len(offline)
        assert all("global_market" not in str(path) for path, _ in online)
        assert all("collectors" not in str(path) for path, _ in offline)


@pytest.mark.parametrize("price", ["0", "-1", "NaN", "Infinity"])
def test_invalid_price_rejected(price):
    with pytest.raises(ValueError):
        refresh.convert("copper", "primary", {
            "date": "2026-09-01", "certificate_irr_per_kg": price,
            "physical_price_irr_per_kg": "100"})


def test_weekly_alignment_retains_quote_age():
    row = refresh.convert("pista", "weekly", {
        "certificate_date": "2026-09-01", "certificate_irr_per_kg": "110",
        "physical_mid_irr_per_kg": "100", "physical_date": "2026-08-28",
        "physical_age_days": "4"})
    assert row["premium_discount_pct"] == "10.0"
    assert row["physical_age_days"] == "4"
    assert row["physical_date"] == "2026-08-28"


def test_failed_builder_prevents_export(monkeypatch):
    monkeypatch.setattr("sys.argv", ["refresh"])
    monkeypatch.setattr(refresh, "plan", lambda *args: [("failing", "local")])
    monkeypatch.setattr(refresh, "load_config", lambda name: (None, {}))
    class Script:
        def relative_to(self, root):
            return "failing"
    monkeypatch.setattr(refresh, "plan", lambda *args: [(Script(), "local")])
    def fail(*args, **kwargs):
        raise RuntimeError("builder failed")
    monkeypatch.setattr(refresh.subprocess, "run", fail)
    monkeypatch.setattr(refresh, "export", lambda name: pytest.fail("Exported failed run"))
    with pytest.raises(RuntimeError, match="builder failed"):
        refresh.main("copper")
