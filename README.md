# BudgetWise Finance Data Cleaning & Analytics

Academic project for **INTE-202 — Integrative Programming and Technologies**. A complete data‑analytics pipeline that cleans a messy finance CSV, computes statistics and trends, aggregates spending by category and month, generates four matplotlib visualisations, and presents everything through a Tkinter GUI.

**Tech stack:** Python 3.11+, pandas, numpy, scipy, matplotlib, Pillow, tkinter.

## Dataset

`budgetwise_finance_dataset.csv` — 15,901 rows × 9 columns:

| Column | Description |
|---|---|
| `transaction_id` | Unique transaction identifier |
| `user_id` | Customer identifier |
| `date` | Transaction date (mixed formats: `2023-04-25`, `08/05/2022`, `31-12-23`) |
| `transaction_type` | `Income` or `Expense` |
| `category` | Spending category (with intentional misspellings: `Educaton`, `Fod`, `rntt`) |
| `amount` | Numeric value (may include currency prefixes like `Rs.828`) |
| `payment_mode` | Payment method (may be abbreviated: `crd`, `csh`) |
| `location` | City name (may be shortened: `BAN`, `HYD`) |
| `notes` | Free‑text memo |

## Repository Structure

```
.
├── budgetwise_finance_dataset.csv      # Raw dataset (15,901 rows)
├── data_cleaning/
│   ├── clean_data.py                   # Standardises categories, parses amounts, removes outliers
│   ├── cleaned_budgetwise_finance_dataset.csv  # Output: cleaned CSV (5,157 rows)
│   └── README.md
├── computations/
│   ├── compute_stats.py                # pandas/NumPy/SciPy stats, correlation, linear forecast
│   ├── statistics_summary.csv          # Output: mean, median, mode, std, min, max, trend params (gitignored)
│   ├── category_frequencies.csv        # Output: category frequency distribution (gitignored)
│   └── README.md
├── data_manipulation/
│   ├── data_analysis.py                # Pandas aggregation: category stats, monthly totals, trend
│   ├── aggregated_budgetwise.csv       # Output: category stats + monthly totals + Pearson r
│   └── README.md
├── visualization/
│   ├── visualize.py                    # 4 matplotlib charts (bar, line, pie, histogram)
│   ├── images/                         # Output: PNG files (gitignored)
│   └── README.md
├── app/
│   ├── app.py                          # Tkinter GUI — 3 tabs: Data, Statistics, Plots
│   └── README.md
├── AGENTS.md                           # Setup & execution guidance for AI coding assistants
└── .gitignore                          # Blocks CSVs under data_*/, computations/*.csv, PNGs, venvs, IDE files
```

## Module Descriptions

- **`data_cleaning/clean_data.py`** — Reads the raw CSV and applies: category normalisation (handles 50+ misspellings like `Educaton`→`Education`, `Fod`→`Food`), amount parsing (`"Rs.828"`→`828.0`) using the fixed regex `r"[-+]?\d+(?:\.\d+)?"`, payment‑mode and location standardisation, date coercion, duplicate removal, and Z‑score outlier filtering (`|z| > 3`). Input/output paths are resolved relative to `__file__`.

- **`computations/compute_stats.py`** — Mixed pandas/NumPy/SciPy approach. `load_amounts_and_dates` uses `pd.read_csv(usecols=[2,5])` for robust CSV parsing; `frequency_distribution` still uses `np.loadtxt(usecols=4)` with hardcoded column indices. Computes basic statistics (mean, median, mode, std, min, max), Pearson correlation between amount and date (continuously-valued), OLS linear regression, and a 30‑day forecast. Outputs `statistics_summary.csv` and `category_frequencies.csv`.

- **`data_manipulation/data_analysis.py`** — Pandas aggregation script. Groups transactions by category (total, average, count, percentage, rank), computes monthly totals via `dt.to_period("M")`, and runs a Pearson correlation on the monthly trend. Outputs a single multi‑section `aggregated_budgetwise.csv`.

- **`visualization/visualize.py`** — Generates four matplotlib figures (all filtered to Expense transactions): bar chart of expenses by category, line chart of monthly expense trend, pie chart of payment‑mode distribution, and histogram of expense amounts. PNGs saved to `visualization/images/` at 300 dpi.

- **`app/app.py`** — Tkinter application with a styled dashboard header (total transactions, total expenses, average amount, date range). Three tabs: **Data** (sortable treeview with batch loading — 200 rows at a time), **Statistics** (on‑demand computation via the sibling `compute_stats` module), **Plots** (invokes the visualisation module and displays the resulting PNGs). Patches `sys.path` to import sibling packages — run as `python app/app.py` from the repo root.

## Prerequisites

- Python 3.11+
- pip (virtual environment recommended)

## Setup

```bash
git clone <repo‑url>
cd ipt_data_cleaning_g1

python -m venv .venv
source .venv/bin/activate   # macOS / Linux

pip install pandas numpy scipy matplotlib pillow
```

## Execution Order (required)

The pipeline has a strict dependency chain. Run scripts **in this order** from the repo root.

```bash
# Step 1 — Clean the raw dataset
python data_cleaning/clean_data.py

# Step 2 — Statistical summary & forecast
python -m computations.compute_stats           # → statistics_summary.csv, category_frequencies.csv

# Step 3 — Category & monthly aggregation
python data_manipulation/data_analysis.py       # → aggregated_budgetwise.csv

# Step 4 — Generate visualisations
python -m visualization.visualize               # → visualization/images/*.png

# Step 5 — Launch GUI
python app/app.py
```

**Important notes:**
- The `python -m` invocation works only for `computations.compute_stats` and `visualization.visualize` (no `__init__.py` in packages).
- Run every command from the repository root; scripts use `__file__`-relative paths.

## Running Individual Steps

| Step | Command | Outputs |
|---|---|---|
| Data cleaning | `python data_cleaning/clean_data.py` | `data_cleaning/cleaned_budgetwise_finance_dataset.csv` |
| Statistics | `python -m computations.compute_stats` | `computations/statistics_summary.csv`, `computations/category_frequencies.csv` |
| Aggregation | `python data_manipulation/data_analysis.py` | `data_manipulation/aggregated_budgetwise.csv` |
| Visualisations | `python -m visualization.visualize` | 4 PNGs in `visualization/images/` |
| GUI | `python app/app.py` | Tkinter window — 3 tabs |

## License

No license file is included. Use at your own discretion.

## Contributing

Feel free to open issues or submit pull requests. Follow standard Python coding conventions (PEP 8, type hints) when adding new functionality.
