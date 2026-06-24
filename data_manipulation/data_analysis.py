'''Data Manipulation Script

This script demonstrates common data manipulation tasks using only pandas, numpy, and scipy on the
cleaned_budgetwise_finance_dataset.csv file.

Operations performed:
- Load CSV with proper date parsing
- Sort by date
- Filter high‑value expenses
- Group by category (total, average, count)
- Compute each category's contribution percentage
- Rank categories by expense total
- Compute monthly totals and a simple trend analysis (Pearson correlation)
- Save aggregated results to a new CSV (different name from source)
''' 

import pathlib
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Current script directory
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
# Path to the cleaned dataset (one level up -> data_cleaning)
DATASET_PATH = CURRENT_DIR.parent / "data_cleaning" / "cleaned_budgetwise_finance_dataset.csv"
# Output path – must differ from the source name
OUTPUT_PATH = CURRENT_DIR / "aggregated_budgetwise.csv"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
# Parse 'date' column as pandas datetime for proper sorting and grouping
df = pd.read_csv(DATASET_PATH, parse_dates=["date"], infer_datetime_format=True)

# ---------------------------------------------------------------------------
# 1. Sorting
# ---------------------------------------------------------------------------
sorted_df = df.sort_values("date")

# ---------------------------------------------------------------------------
# 2. Filtering – example: keep only expense transactions > $1,000
# ---------------------------------------------------------------------------
high_value_expenses = df[(df["transaction_type"] == "Expense") & (df["amount"] > 1_000)]

# ---------------------------------------------------------------------------
# 3. Grouping & Aggregation by 'category'
# ---------------------------------------------------------------------------
category_stats = (
    df.groupby("category", as_index=False)
    .agg(
        total_amount=pd.NamedAgg(column="amount", aggfunc="sum"),
        average_amount=pd.NamedAgg(column="amount", aggfunc="mean"),
        transaction_count=pd.NamedAgg(column="transaction_id", aggfunc="count"),
    )
)
# Percentage of overall amount contributed by each category
overall_total = df["amount"].sum()
category_stats["percentage_of_total"] = (category_stats["total_amount"] / overall_total) * 100
# Rank categories by total_amount (1 = highest)
category_stats["rank"] = category_stats["total_amount"].rank(method="dense", ascending=False).astype(int)

# ---------------------------------------------------------------------------
# 4. Monthly Totals
# ---------------------------------------------------------------------------
# Create a Year-Month period column for grouping
df["year_month"] = df["date"].dt.to_period("M")
monthly_totals = (
    df.groupby("year_month", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "monthly_total"})
)
# Convert period to string for easier CSV output
monthly_totals["year_month"] = monthly_totals["year_month"].astype(str)

# ---------------------------------------------------------------------------
# 5. Simple Trend Analysis (Pearson correlation)
# ---------------------------------------------------------------------------
# Encode each month as an integer (ordinal) to compute correlation with total amount
monthly_totals["month_index"] = np.arange(len(monthly_totals))
if len(monthly_totals) > 1:
    corr_coef, p_value = pearsonr(monthly_totals["month_index"], monthly_totals["monthly_total"])
else:
    corr_coef, p_value = np.nan, np.nan

# ---------------------------------------------------------------------------
# 6. Save aggregated results
# ---------------------------------------------------------------------------
# Combine category and monthly summaries into a single Excel‑style CSV for easy inspection
with open(OUTPUT_PATH, "w", newline="") as f:
    f.write("# Category Aggregation\n")
    category_stats.to_csv(f, index=False)
    f.write("\n# Monthly Totals\n")
    monthly_totals.to_csv(f, index=False)
    f.write("\n# Trend Summary\n")
    f.write(f"pearson_correlation, p_value\n{corr_coef}, {p_value}\n")

# ---------------------------------------------------------------------------
# 7. Example console output (optional when script is run directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Sorted by date (first 5 rows) ===")
    print(sorted_df.head())
    print("\n=== High‑value expenses (> $1,000) count:", len(high_value_expenses))
    print("\n=== Category Stats (top 5 by total) ===")
    print(category_stats.sort_values("total_amount", ascending=False).head())
    print("\n=== Monthly Totals (first 5) ===")
    print(monthly_totals.head())
    print("\n=== Trend (Pearson correlation) ===")
    print(f"Correlation coefficient: {corr_coef:.4f}, p‑value: {p_value:.4g}")
    print(f"Saved aggregated data to {OUTPUT_PATH}")
