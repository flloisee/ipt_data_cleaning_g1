# `data_cleaning/` — Raw Dataset Sanitisation

This is the **entry point** of the pipeline. It reads the raw 15,901-row CSV (`budgetwise_finance_dataset.csv` from the repo root) and applies a thorough cleaning pass using **pandas**, **numpy**, and **scipy**. The output is a standardised, outlier-free CSV consumed by every subsequent module.

## Cleaning operations (in order)

| Step | Detail |
|------|--------|
| **Drop missing critical fields** | Rows where `date` or `category` are `NaN` are removed entirely. |
| **Normalise notes** | Whitespace-only notes → `NaN` → filled with `"N/A"`. |
| **Standardise categories** | `clean_category()` maps 50+ misspellings (*Educaton*, *Fod*, *rntt*, *entrtnmnt*, *utlities*, *helth*, etc.) to a canonical set: *Education*, *Rent*, *Food*, *Entertainment*, *Travel*, *Utilities*, *Health*, *Salary*, *Investment*, *Freelance*, *Bonus*, *Savings*, *Others*, *Misc*. |
| **Parse amounts** | `clean_amount()` strips currency prefixes (`Rs.828` → `828.0`), handles commas, and extracts the first numeric match. |
| **Normalise payment modes** | `clean_payment_mode()` maps *crd*→*Card*, *csh*→*Cash*, *upi*→*UPI*, any mention of *bank*→*Bank Transfer*, fallback→*Unknown*. |
| **Normalise locations** | `clean_location()` expands abbreviations (*BAN*→*Bangalore*, *HYD*→*Hyderabad*, *AHM*→*Ahmedabad*, etc.) and title-cases unknown values. |
| **Date coercion** | `pd.to_datetime(..., infer_datetime_format=True)` handles mixed formats (`2023-04-25`, `08/05/2022`, `31-12-23`). Rows that fail parsing are dropped. |
| **Remove invalid amounts** | Non-numeric, `<= 0`, and `>= 100000` rows are dropped. |
| **Deduplication** | Full-row duplicates are removed. |
| **Z-score outlier filter** | Computes the Z-score (`scipy.stats.zscore`) for every value in the `amount` column, measuring how many standard deviations it lies from the mean. Rows where `|z| > 3` (beyond 3σ) are discarded — this removes extreme outliers while preserving ~99.7% of normally distributed data. Applied after all other cleaning steps so the mean and std are not skewed by invalid entries. |

## Output

- `cleaned_budgetwise_finance_dataset.csv` — the cleaned dataset (gitignored).

## Dependencies

pandas, numpy, scipy.

## Run

```bash
python data_cleaning/clean_data.py
```
