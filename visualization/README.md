# `visualization/` — Matplotlib Chart Generation

This module generates **four publication-quality matplotlib figures** from the cleaned dataset, all filtered to **Expense** transactions only. PNGs are saved to `visualization/images/` at 300 dpi.

## Script: `visualize.py`

### Charts produced

| File | Chart type | Description |
|------|-----------|-------------|
| `category_bar.png` | Vertical bar | Total expense amount per category, sorted descending. |
| `monthly_expense_line.png` | Line | Monthly total expenses over time (PeriodIndex → timestamp, up to 12 x-axis ticks). |
| `payment_mode_pie.png` | Pie | Distribution of expenses by payment mode (Card, Cash, UPI, Bank Transfer) with percentage labels. |
| `expense_amount_hist.png` | Histogram | Distribution of individual expense amounts (30 bins, salmon-coloured). |

### Key details

- All charts are expense-only (`df["transaction_type"] == "Expense"`).
- `os.makedirs(IMG_DIR, exist_ok=True)` ensures the output directory exists.
- Uses `MaxNLocator` for sane tick density on the line chart.
- Tight layout (`plt.tight_layout()`) prevents label clipping.

### Dependencies

pandas, matplotlib, Pillow (for image display in the GUI app).

### Run

```bash
python -m visualization.visualize
```

The `-m` flag is required because there is no `__init__.py` in this package.

### Image directory

Output PNGs are written to `visualization/images/`. This directory and all `*.png` files are gitignored.
