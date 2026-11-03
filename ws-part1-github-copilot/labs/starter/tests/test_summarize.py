import subprocess
import sys
from pathlib import Path

import pytest

from summarize import load_rows, summarize, top_region


STARTER = Path(__file__).resolve().parents[1]
DATA = STARTER / "data"


def run_report(*args):
    return subprocess.run([sys.executable, str(STARTER / "summarize.py"), *map(str, args)],
                          capture_output=True, text=True)


def test_load_sales():
    rows = load_rows(DATA / "sales.csv")
    assert len(rows) == 4
    assert rows[0] == {"region": "East", "amount": "100"}


def test_load_rows_trims_region_names(tmp_path):
    path = tmp_path / "whitespace.csv"
    path.write_text("region,amount\n  East  ,100\n", encoding="utf-8")

    assert load_rows(path) == [{"region": "East", "amount": "100"}]


@pytest.mark.parametrize(
    ("path", "message", "line_number"),
    [
        (DATA / "invalid-amount.csv", "amount must be a number", 3),
        (DATA / "missing-column.csv", "missing required column", None),
    ],
)
def test_supplied_invalid_files_fail_cleanly(path, message, line_number):
    result = run_report(path)

    assert result.returncode != 0
    assert result.stdout == ""
    assert message in result.stderr
    assert "Traceback" not in result.stderr
    if line_number is not None:
        assert f"line {line_number}" in result.stderr


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("region,amount\n   ,10\n", "line 2: region must not be blank"),
        ("region,amount\nEast,nan\n", "line 2: amount must be finite"),
        ("region,amount\nEast,inf\n", "line 2: amount must be finite"),
        ("region,amount\nEast,-1\n", "line 2: amount must not be negative"),
        ("region,amount\nEast\n", "line 2: expected 2 columns, found 1"),
        ("region,amount\nEast,100,extra\n", "line 2: expected 2 columns, found 3"),
    ],
)
def test_invalid_rows_fail_cleanly(tmp_path, content, message):
    path = tmp_path / "invalid.csv"
    path.write_text(content, encoding="utf-8")

    result = run_report(path)

    assert result.returncode != 0
    assert result.stdout == ""
    assert message in result.stderr
    assert "Traceback" not in result.stderr


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


def test_region_filter_east():
    result = run_report(DATA / "sales.csv", "--region", "East")
    assert result.returncode == 0
    assert result.stdout == "East: 150.00\nAverage per region: 150.00\n"


def test_region_filter_unknown_fails_cleanly():
    result = run_report(DATA / "sales.csv", "--region", "Unknown")
    assert result.returncode != 0
    assert result.stdout == ""
    assert "unknown region" in result.stderr
    assert "Traceback" not in result.stderr


def test_default_report_unchanged():
    result = run_report(DATA / "sales.csv")
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["East: 150.00", "North: 75.00", "West: 250.00", "Average per region: 158.33"]
