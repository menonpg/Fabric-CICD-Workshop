from pathlib import Path

import pytest

from summarize import load_rows, summarize, top_region


DATA = Path(__file__).resolve().parents[1] / "data"


def test_load_sales():
    rows = load_rows(DATA / "sales.csv")
    assert len(rows) == 4
    assert rows[0] == {"region": "East", "amount": "100"}


def test_totals_by_region():
    totals, _ = summarize(load_rows(DATA / "sales.csv"))
    assert totals == {"East": 150.0, "West": 250.0, "North": 75.0}


def test_top_region_normal():
    assert top_region({"East": 150, "West": 250}) == ("West", 250)


def test_top_region_tie_breaks_alphabetically():
    # West listed first so taking the first maximum would wrongly pass
    assert top_region({"West": 200, "East": 200}) == ("East", 200)


def test_top_region_empty():
    assert top_region({}) is None


def test_average_is_mean_of_regional_totals():
    # 475 total across 3 regions; averaging per row (4 rows) would give 118.75
    _, average = summarize(load_rows(DATA / "sales.csv"))
    assert average == pytest.approx(475 / 3)
