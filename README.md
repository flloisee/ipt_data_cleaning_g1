# Real‑Life Data Analytics System using Python

## Overview
This repository implements a complete data‑analytics workflow for a finance dataset. It demonstrates:
- Data cleaning and preprocessing
- Data manipulation and aggregation
- Statistical analysis and forecasting
- Generation of visualisations
- A Tkinter‑based GUI for interactive exploration

All code is written in Python 3.11+ and uses popular data‑science libraries.

## Repository Structure
- `budgetwise_finance_dataset.csv` – original raw dataset (≥ 500 rows, 6+ columns).
- `data_cleaning/clean_data.py` – script that cleans the raw CSV and produces `cleaned_budgetwise_finance_dataset.csv`.
- `data_cleaning/cleaned_budgetwise_finance_dataset.csv` – cleaned version used by downstream scripts.
- `computations/compute_stats.py` – statistical summary, correlation, trend and forecast generation.
- `data_manipulation/data_analysis.py` – aggregation, category ranking and monthly trend analysis.
- `visualization/visualize.py` – matplotlib visualisations saved under `visualization/images/`.
- `visualization/images/` – PNG files produced by the visualisation script.
- `app/app.py` – Tkinter GUI that displays the cleaned data, statistics and visualisations.


- `FINAL‑PROJECT‑REQUIREMENTS‑INTE‑202‑Integrative‑Programming‑and‑Technologies.pdf` – assignment specification.

## Prerequisites
- Python 3.11 or newer
- pip (or a virtual‑environment manager)

## Installation
```bash
# Clone the repository (if you haven't already)
git clone <repo‑url>
cd ipt_data_cleaning_g1

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate.bat # Windows

# Install required libraries
pip install pandas numpy scipy matplotlib pillow
```

## VSCode

- You can also run the Python scripts directly from VSCode's integrated terminal or by right‑clicking a script and selecting **Run Python File in Terminal**.

## Data Preparation
1. Ensure `budgetwise_finance_dataset.csv` is present in the repository root.
2. Run the cleaning script to produce a cleaned CSV:
```bash
python data_cleaning/clean_data.py
```
The cleaned file will be written to `data_cleaning/cleaned_budgetwise_finance_dataset.csv`.

## Running the Analyses
- **Statistical summary & forecast**
```bash
python -m computations.compute_stats
```
Outputs `statistics_summary.csv` and `category_frequencies.csv` in `computations/`.

- **Aggregation & monthly trend**
```bash
python data_manipulation/data_analysis.py
```
Creates `aggregated_budgetwise.csv` with category and monthly summaries.

- **Generate visualisations**
```bash
python -m visualization.visualize
```
Four PNG files are saved under `visualization/images/`.

## GUI Application
Launch the interactive desktop application:
```bash
python app/app.py
```
The window provides three tabs:
- **Data** – sortable table view of the cleaned dataset.
- **Statistics** – on‑demand numeric summaries.
- **Plots** – displays the four pre‑generated visualisations.



## License
No license file is included. Use at your own discretion.

## Contributing
Feel free to open issues or submit pull requests. Follow standard Python coding conventions (PEP 8, type hints) when adding new functionality.
