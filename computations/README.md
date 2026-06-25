# `computations/` — Numerical Statistics & Trend Analysis

This module performs **pure NumPy/SciPy** computations (no pandas) on the cleaned dataset. It loads data via `np.loadtxt` with **hardcoded column indices** (2=date, 4=category, 5=amount) — a design constraint that means any CSV schema change must be mirrored here.

## Script: `compute_stats.py`

### What it does

1. **Loads amounts & dates** from the cleaned CSV using `np.loadtxt`, converting date strings to `datetime64[D]` then to days-since-epoch integers for correlation.
2. **Basic statistics**: mean, median, mode, sample standard deviation (`ddof=1`), min, max.
3. **Pearson correlation** between `amount` and `date` — quantifies whether transaction values trend over time.
4. **OLS linear regression** (`scipy.stats.linregress`) — slope, intercept, R-value, p-value, standard error.
5. **30-day forecast** — projects the next amount value using the linear trend line.
6. **Category frequency distribution** — counts unique values in the `category` column using `np.unique(..., return_counts=True)`.

### Outputs

| File | Contents |
|------|----------|
| `statistics_summary.csv` | Metric-value pairs: mean, median, mode, std_dev, min, max, correlation, trend params, 30-day forecast. |
| `category_frequencies.csv` | Category → count distribution. |

### Key detail

Column indices are hardcoded in `np.loadtxt` calls — if the CSV column order ever changes, update `usecols=5` (amount), `usecols=2` (date), and `usecols=4` (category) in the source.

### Dependencies

numpy, scipy.

### Run

```bash
python -m computations.compute_stats
```

The `-m` flag is required because there is no `__init__.py` in this package.
