---
name: summarize-csv
description: "Run the starter sales report on a CSV and explain the totals and the average per region."
---
1. Read `ws-part1-github-copilot/labs/starter/README.md` for the business rules.
2. From `ws-part1-github-copilot/labs/starter`, run `python summarize.py data/sales.csv` with the starter's interpreter,
   and `python -m pytest -q`.
3. Explain the output: totals are summed by region; the average is the mean of the **regional totals** (for the sample
   data 475 / 3 = 158.33), not the mean of individual sales.
4. Do not silently fix unrelated code; report problems instead.
