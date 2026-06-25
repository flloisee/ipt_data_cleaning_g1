# `app/` — Tkinter GUI Dashboard

The **front-end** of the pipeline — a Tkinter application (`FinanceApp`) that ties together the outputs from all previous modules into a single interactive dashboard. It patches `sys.path` at startup to import sibling modules (`visualization.visualize` and `computations.compute_stats`).

## Script: `app.py`

### Features

| Feature | Details |
|---------|---------|
| **Header bar** | Dark navy strip with four metric cards: *Total Transactions*, *Total Expenses*, *Average Amount*, *Date Range*. |
| **Data tab** | Sortable `ttk.Treeview` table showing all columns. Batch loading (200 rows + *Load More* / *Load All* buttons). Column headings click to sort ▲/▼ with mergesort. Zebra-striped rows. |
| **Statistics tab** | On-demand computation. Click *Compute Statistics* to run the `compute_stats` module and display: basic stats, correlation/trend parameters (including a 30-day forecast), and a category frequency table. Results appear in styled `LabelFrame` cards. |
| **Plots tab** | Click *Generate Plots* to invoke the `visualize` module (overwrites existing PNGs), then displays each chart in a scrollable card with a caption. Images are resized to 800×600 via Pillow `thumbnail` (LANCZOS filtering). |

### Batch loading

The Data tab loads only 200 rows initially. Scrolling reveals *Load More* (+200) and *Load All* buttons. The sorting state (column + direction) is preserved across batch loads.

### Mouse wheel scrolling

The Plots tab supports macOS (small delta), Windows (multiple-of-120 delta), and Linux (Button-4/5) scroll events.

### Dependencies

pandas, Pillow. At runtime it calls into `visualization.visualize` (matplotlib, pandas) and `computations.compute_stats` (numpy, scipy).

### Run

```bash
python app/app.py
```

Must be executed from the repository root so that the `sys.path` patch resolves sibling packages correctly.
