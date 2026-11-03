import argparse
import csv
from typing import Dict, Optional, Tuple


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def summarize(rows):
    totals = {}
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
    args = parser.parse_args()
    try:
        totals, average = summarize(load_rows(args.path))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    for region, amount in sorted(totals.items()):
        print(f"{region}: {amount:.2f}")
    print(f"Average per region: {average:.2f}")


if __name__ == "__main__":
    main()
