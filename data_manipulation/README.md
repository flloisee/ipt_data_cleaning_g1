# `data_manipulation/` — Pandas Aggregation & Analysis

This module uses **pandas** (with numpy and scipy) to reshape and summarise the cleaned dataset. It produces a single multi-section CSV that combines category-level statistics, monthly time-series totals, and a trend correlation.

## Script: `data_analysis.py`

### Operations performed

| Step | Description |
|------|-------------|
| **Load & parse** | `pd.read_csv` with `parse_dates=["date"]` for proper datetime handling. |
| **Sort** | DataFrame sorted by `date`. |
| **Filter** | High-value expenses (`transaction_type == "Expense"` and `amount > 1,000`). |
| **Category aggregation** | Groups by `category` and computes: `total_amount`, `average_amount`, `transaction_count`, `percentage_of_total` (share of overall spend), and `rank` (by total descending). |
| **Monthly totals** | Extracts `year_month` via `dt.to_period("M")`, groups by it, and sums amounts. |
| **Trend analysis** | Encodes months as ordinal integers and runs a **Pearson correlation** (`scipy.stats.pearsonr`) against monthly totals to detect monotonic trends. |

### Output

- `aggregated_budgetwise.csv` — a single CSV with three labelled sections:
  1. **Category Aggregation** — per-category totals, averages, counts, percentages, ranks.
  2. **Monthly Totals** — year-month → total spend.
  3. **Trend Summary** — Pearson correlation coefficient and p-value.

### Dependencies

pandas, numpy, scipy.

### Run

```bash
python data_manipulation/data_analysis.py
```
