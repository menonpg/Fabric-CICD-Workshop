import argparse
import csv
import math
from typing import Dict, List, Optional, Tuple


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.reader(source, strict=True)
        try:
            headers = next(reader, None)
        except csv.Error as error:
            raise ValueError(f"line {reader.line_num}: malformed CSV: {error}") from error
        if headers is None:
            headers = []
        missing = [column for column in ("region", "amount") if column not in headers]
        if missing:
            raise ValueError(f"CSV missing required column(s): {', '.join(missing)}")

        while True:
            line_number = reader.line_num + 1
            try:
                values = next(reader)
            except StopIteration:
                break
            except csv.Error as error:
                raise ValueError(f"line {reader.line_num}: malformed CSV: {error}") from error
            if len(values) != len(headers):
                raise ValueError(
                    f"line {line_number}: expected {len(headers)} columns, found {len(values)}"
                )

            row = dict(zip(headers, values))
            row["region"] = row["region"].strip()
            if not row["region"]:
                raise ValueError(f"line {line_number}: region must not be blank")
            try:
                amount = float(row["amount"])
            except ValueError as error:
                raise ValueError(
                    f"line {line_number}: amount must be a number, got {row['amount']!r}"
                ) from error
            if not math.isfinite(amount):
                raise ValueError(f"line {line_number}: amount must be finite")
            if amount < 0:
                raise ValueError(f"line {line_number}: amount must not be negative")
            rows.append(row)
    return rows


def summarize(rows: List[Dict[str, str]]) -> Tuple[Dict[str, float], float]:
    """Total the amounts by region and return (totals, average of the regional totals)."""
    totals: Dict[str, float] = {}
    for row in rows:
        region = row["region"]
        totals[region] = totals.get(region, 0) + float(row["amount"])
    average = sum(totals.values()) / len(totals)
    return totals, average


def top_region(totals: Dict[str, float]) -> Optional[Tuple[str, float]]:
    """Return the (region, amount) with the highest total, or None if there are no totals.

    Ties are broken alphabetically by region name.
    """
    # Return the highest-total region and amount; break ties alphabetically.
    if not totals:
        return None
    region = min(totals, key=lambda name: (-totals[name], name))
    return region, totals[region]


def main():
    parser = argparse.ArgumentParser(description="Summarize sales by region.")
    parser.add_argument("path", help="Path to the sales CSV")
    parser.add_argument("--region", help="Report only this region (case-sensitive)")
    args = parser.parse_args()
    try:
        rows = load_rows(args.path)
        if args.region is not None:
            rows = [row for row in rows if row["region"] == args.region]
            if not rows:
                raise ValueError(f"unknown region '{args.region}'")
        totals, average = summarize(rows)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    for region, amount in sorted(totals.items()):
        print(f"{region}: {amount:.2f}")
    print(f"Average per region: {average:.2f}")


if __name__ == "__main__":
    main()
