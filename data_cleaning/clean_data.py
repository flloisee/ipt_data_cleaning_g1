"""Data cleaning script for budgetwise finance dataset.

This script demonstrates common data cleaning techniques required for the project:
- Handling missing values (date, category, notes)
- Removing duplicate rows
- Correcting inconsistent entries (category names, amount formats)
- Renaming columns (none needed – the original headers are already clear)
- Converting data types (date to datetime, amount to numeric)
- Filtering invalid data (rows with missing critical fields, non‑numeric amounts)
- Handling outliers in the `amount` column using Z‑score from SciPy

The script follows the exact specifications given in the assignment and uses only `numpy`, `pandas` and `scipy`.
"""

import re
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

def clean_category(cat):
    """Standardize the `category` column to a fixed set of values."""
    if pd.isna(cat):
        return np.nan
    s = str(cat).strip().lower()
    # Education variants
    if "educat" in s or "edu" in s:
        return "Education"
    # Rent variants (including common misspellings)
    if any(x in s for x in ("rent", "rnt", "rntt")):
        return "Rent"
    # Food variants (including common misspellings)
    if any(x in s for x in ("food", "fod", "foodd", "foods", "foodd")):
        return "Food"
    # Entertainment variants
    if any(x in s for x in ("entertain", "entert", "ent", "entrtnmnt", "entertainm", "entertn")):
        return "Entertainment"
    # Travel variants
    if any(x in s for x in ("travel", "travl", "traval", "trav", "trvl")):
        return "Travel"
    # Utilities variants
    if any(x in s for x in ("util", "utl", "utlities", "utility", "utilities")):
        return "Utilities"
    # Health variants
    if any(x in s for x in ("health", "helth")):
        return "Health"
    if "salary" in s:
        return "Salary"
    if "investment" in s:
        return "Investment"
    if "freelance" in s:
        return "Freelance"
    if "bonus" in s:
        return "Bonus"
    if "saving" in s:
        return "Savings"
    if "other" in s:
        return "Others"
    if "misc" in s:
        return "Misc"
    # Fallback – title case the original value
    return cat.title()

def clean_amount(val):
    """Extract a numeric value from messy amount strings (e.g. 'Rs.828', '$1234')."""
    if pd.isna(val):
        return np.nan
    s = str(val).replace(",", "")
    numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+", s)
    if not numbers:
        return np.nan
    try:
        return float(numbers[0])
    except ValueError:
        return np.nan

def clean_payment_mode(pm):
    """Standardize payment mode values to Card, Cash, UPI, Bank Transfer, Unknown."""
    if pd.isna(pm):
        return "Unknown"
    s = str(pm).strip().lower()
    # Card variants
    if "card" in s or "crd" in s:
        return "Card"
    # Cash variants
    if "cash" in s or "csh" in s:
        return "Cash"
    # UPI variants
    if "upi" in s:
        return "UPI"
    # Bank transfer variants (any mention of bank)
    if "bank" in s:
        return "Bank Transfer"
    # Fallback – title case
    return pm.title()

def clean_location(loc):
    """Standardize location values to canonical city names."""
    if pd.isna(loc) or loc == "nan":
        return "Unknown"
    s = str(loc).strip().lower()
    # Ahmedabad variants
    if s in ("ahm", "ahmedabad"):
        return "Ahmedabad"
    # Bangalore variants
    if s in ("bangalore", "ban"):
        return "Bangalore"
    # Delhi variants
    if s in ("delhi", "del", "delhi"):
        return "Delhi"
    # Hyderabad variants
    if s in ("hyderabad", "hyd"):
        return "Hyderabad"
    # Mumbai variants
    if s in ("mumbai", "mum", "mum"):
        return "Mumbai"
    # Pune variants
    if s in ("pune", "pun", "pune"):
        return "Pune"
    # Kolkata variants
    if s in ("kolkata", "kol", "kolkata"):
        return "Kolkata"
    # Lucknow variants
    if s in ("lucknow", "luc"):
        return "Lucknow"
    # Jaipur variants
    if s in ("jaipur", "jai", "jaipur"):
        return "Jaipur"
    # Chennai variants
    if s in ("chennai", "che"):
        return "Chennai"
    # Fallback – title case
    return loc.title()


def main():
    script_dir = Path(__file__).parent
    input_path = script_dir.parent / "budgetwise_finance_dataset.csv"
    df = pd.read_csv(input_path)
    df = df.dropna(subset=["date"])
    df = df.dropna(subset=["category"])
    # Replace empty or whitespace-only notes with NaN then fill with "N/A"
    df["notes"] = df["notes"].replace(r'^\s*$', np.nan, regex=True).fillna("N/A")
    df["category"] = df["category"].apply(clean_category)
    df["amount"] = df["amount"].apply(clean_amount)
    # Normalize payment mode and location
    df["payment_mode"] = df["payment_mode"].apply(clean_payment_mode)
    df["location"] = df["location"].apply(clean_location)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", infer_datetime_format=True)
    df = df.dropna(subset=["date"])
    df = df.dropna(subset=["amount"])
    # Remove non-positive amounts
    df = df[df["amount"] > 0]
    # Remove extremely large amounts (threshold 100000)
    df = df[df["amount"] < 100000]
    # Remove duplicate rows
    df = df.drop_duplicates()
    # Remove statistical outliers using Z-score (threshold 3)
    if not df.empty:
        z_scores = np.abs(stats.zscore(df["amount"]))
        df = df[z_scores < 3]
    df["transaction_id"] = df["transaction_id"].astype(str)
    df["user_id"] = df["user_id"].astype(str)
    df["transaction_type"] = df["transaction_type"].astype(str)
    df["category"] = df["category"].astype(str)
    df["payment_mode"] = df["payment_mode"].astype(str)
    df["location"] = df["location"].astype(str)
    # Ensure any missing notes are filled with N/A (safety)
    df["notes"] = df["notes"].replace(r'^\s*$', np.nan, regex=True).fillna("N/A")
    output_path = script_dir / "cleaned_budgetwise_finance_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"Cleaning complete. Cleaned file saved to: {output_path}")

if __name__ == "__main__":
    main()
