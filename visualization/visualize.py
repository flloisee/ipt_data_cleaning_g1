'''visualize.py

Generate required visualizations using matplotlib.
'''  # noqa: D400

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Constants
DATA_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "data_cleaning", "cleaned_budgetwise_finance_dataset.csv"
    )
)
IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "images"))

# Ensure the output directory exists
os.makedirs(IMG_DIR, exist_ok=True)

def load_data() -> pd.DataFrame:
    """Load the cleaned finance dataset.

    Returns
    -------
    pd.DataFrame
        DataFrame with parsed dates.
    """
    df = pd.read_csv(DATA_PATH, parse_dates=["date"], infer_datetime_format=True)
    # Ensure numeric amount (some rows may have missing/invalid values)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    return df

def bar_expenses_by_category(df: pd.DataFrame) -> None:
    """Bar chart of total expense amount per category.
    Saves the figure to ``category_bar.png``.
    """
    expenses = df[df["transaction_type"] == "Expense"]
    # Group by category and sum amounts
    cat_sum = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    cat_sum.plot(kind="bar", color="steelblue")
    plt.title("Total Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_path = os.path.join(IMG_DIR, "category_bar.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

def line_monthly_expense_trend(df: pd.DataFrame) -> None:
    """Line plot of monthly total expenses.
    Saves the figure to ``monthly_expense_line.png``.
    """
    expenses = df[df["transaction_type"] == "Expense"].copy()
    expenses["year_month"] = expenses["date"].dt.to_period("M")
    monthly = expenses.groupby("year_month")["amount"].sum()
    # Convert PeriodIndex to timestamps for plotting
    monthly_index = monthly.index.to_timestamp()
    plt.figure(figsize=(12, 6))
    plt.plot(monthly_index, monthly.values, marker="o", linestyle="-")
    plt.title("Monthly Expense Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Expense (₹)")
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True))
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    out_path = os.path.join(IMG_DIR, "monthly_expense_line.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

def pie_payment_mode_distribution(df: pd.DataFrame) -> None:
    """Pie chart of payment mode distribution for expenses.
    Saves the figure to ``payment_mode_pie.png``.
    """
    expenses = df[df["transaction_type"] == "Expense"]
    mode_counts = expenses["payment_mode"].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(
        mode_counts.values,
        labels=mode_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=plt.cm.Paired.colors,
    )
    plt.title("Expense Payment Mode Distribution")
    plt.tight_layout()
    out_path = os.path.join(IMG_DIR, "payment_mode_pie.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

def histogram_expense_amount(df: pd.DataFrame) -> None:
    """Histogram of expense amounts.
    Saves the figure to ``expense_amount_hist.png``.
    """
    expenses = df[df["transaction_type"] == "Expense"]
    plt.figure(figsize=(10, 6))
    plt.hist(expenses["amount"].dropna(), bins=30, color="salmon", edgecolor="black")
    plt.title("Distribution of Expense Amounts")
    plt.xlabel("Amount (₹)")
    plt.ylabel("Number of Transactions")
    plt.tight_layout()
    out_path = os.path.join(IMG_DIR, "expense_amount_hist.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

def main() -> None:
    df = load_data()
    bar_expenses_by_category(df)
    line_monthly_expense_trend(df)
    pie_payment_mode_distribution(df)
    histogram_expense_amount(df)
    print(f"Visualizations saved to {IMG_DIR}")

if __name__ == "__main__":
    main()
