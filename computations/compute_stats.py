import os
import csv
import pandas as pd
import numpy as np
from scipy import stats

# Path to the cleaned dataset CSV (relative to this script)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data_cleaning", "cleaned_budgetwise_finance_dataset.csv")

def load_amounts_and_dates(csv_path):
    """Load numeric amount column and date column as numpy arrays.
    Returns:
        amounts (np.ndarray): float64 array of transaction amounts.
        dates_int (np.ndarray): int64 array representing dates as days since epoch.
    """
    df = pd.read_csv(csv_path, usecols=[2, 5], parse_dates=["date"])
    amounts = df["amount"].to_numpy(dtype=np.float64)
    dates = df["date"].to_numpy(dtype="datetime64[D]")
    dates_int = dates.astype("int64")  # days since epoch for correlation
    return amounts, dates_int

def compute_basic_stats(amounts):
    """Compute mean, median, mode, std deviation, min, max for a 1‑D array.
    Returns a dict of metric names to values.
    """
    mean = np.mean(amounts)
    median = np.median(amounts)
    # scipy.stats.mode returns the modal value and its count. For 1‑D data it returns the smallest mode.
    mode_res = stats.mode(amounts, keepdims=False)
    mode_val = mode_res.mode if np.isscalar(mode_res.mode) else mode_res.mode[0]
    std_dev = np.std(amounts, ddof=1)  # sample standard deviation
    min_val = np.min(amounts)
    max_val = np.max(amounts)
    return {
        "mean": mean,
        "median": median,
        "mode": float(mode_val),
        "std_dev": std_dev,
        "min": min_val,
        "max": max_val,
    }

def compute_correlation_and_trend(amounts, dates_int):
    """Return Pearson correlation between amount and date, and linear trend parameters.
    The trend is computed using ordinary least squares (scipy.stats.linregress).
    Returns a dict with keys: correlation, slope, intercept, r_value, p_value, std_err.
    """
    correlation = np.corrcoef(amounts, dates_int)[0, 1]
    slope, intercept, r_value, p_value, std_err = stats.linregress(dates_int, amounts)
    return {
        "correlation": correlation,
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "std_err": std_err,
    }

def frequency_distribution(csv_path, column_index=4):
    """Compute frequency distribution for a categorical column.
    Default column_index=4 corresponds to the 'category' column in the budget dataset.
    Returns two parallel lists: unique categories and their counts.
    """
    categories = np.loadtxt(csv_path, delimiter=",", dtype=str, skiprows=1, usecols=column_index)
    uniq, counts = np.unique(categories, return_counts=True)
    return uniq.tolist(), counts.tolist()

def forecast_next_amount(trend_info, last_date_int, days_ahead=30):
    """Forecast amount using the linear trend.
    Args:
        trend_info (dict): output of compute_correlation_and_trend.
        last_date_int (int): numeric representation of the most recent date.
        days_ahead (int): how many days into the future to predict.
    Returns:
        float forecasted amount.
    """
    future_date = last_date_int + days_ahead
    return trend_info["slope"] * future_date + trend_info["intercept"]

def write_summary_csv(stats_dict, correlation_dict, forecast, output_path):
    """Write a simple CSV summarising numeric statistics and trend information.
    The file will have two columns: metric, value.
    """
    with open(output_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for k, v in stats_dict.items():
            writer.writerow([k, v])
        writer.writerow(["correlation_amount_date", correlation_dict["correlation"]])
        writer.writerow(["trend_slope", correlation_dict["slope"]])
        writer.writerow(["trend_intercept", correlation_dict["intercept"]])
        writer.writerow(["forecast_next_30_days", forecast])

def write_category_frequencies(categories, counts, output_path):
    """Write category frequencies to a CSV file.
    Columns: category, count
    """
    with open(output_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "count"])
        for cat, cnt in zip(categories, counts):
            writer.writerow([cat, cnt])

def main():
    amounts, dates_int = load_amounts_and_dates(DATA_PATH)
    basic_stats = compute_basic_stats(amounts)
    corr_trend = compute_correlation_and_trend(amounts, dates_int)
    # Forecast amount 30 days after the most recent transaction date
    forecast = forecast_next_amount(corr_trend, dates_int.max(), days_ahead=30)
    # Frequency distribution for the 'category' column (index 4)
    categories, counts = frequency_distribution(DATA_PATH, column_index=4)

    # Write results to CSV files in the same folder as this script
    summary_path = os.path.join(os.path.dirname(__file__), "statistics_summary.csv")
    cat_path = os.path.join(os.path.dirname(__file__), "category_frequencies.csv")
    write_summary_csv(basic_stats, corr_trend, forecast, summary_path)
    write_category_frequencies(categories, counts, cat_path)
    print("Statistics and frequency files written to:")
    print(summary_path)
    print(cat_path)

if __name__ == "__main__":
    main()
