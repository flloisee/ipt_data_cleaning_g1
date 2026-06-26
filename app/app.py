'''Finance Analytics GUI Application

This application provides a Tkinter based graphical interface to:
- Load and display the cleaned finance dataset in a table view.
- Compute and present basic statistical summaries and simple trend analysis.
- Generate a set of predefined visualisations (bars, line, pie, histogram) and display them.

The implementation reuses the existing helper modules in the repository:
- ``visualization.visualize`` for creating the plots.
- ``computations.compute_stats`` for statistical calculations.

The code is deliberately kept compact while still being clear, type‑annotated and
structured for easy maintenance.
'''  # noqa: D400

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# Pillow for image resizing
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# --- Make repository modules importable ------------------------------------
# The script lives in ``cleaning_main/app``; the repository root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import helper functions from sibling packages.
from visualization.visualize import (
    load_data as viz_load_data,
    bar_expenses_by_category,
    line_monthly_expense_trend,
    pie_payment_mode_distribution,
    histogram_expense_amount,
)
from computations.compute_stats import (
    load_amounts_and_dates,
    compute_basic_stats,
    compute_correlation_and_trend,
    frequency_distribution,
)

# ---------------------------------------------------------------------------
# Paths used throughout the app
# ---------------------------------------------------------------------------
CLEANED_DATA_PATH = REPO_ROOT / "data_cleaning" / "cleaned_budgetwise_finance_dataset.csv"
VIS_IMG_DIR = REPO_ROOT / "visualization" / "images"

# Ensure the image directory exists (visualisation module creates it on import).
VIS_IMG_DIR.mkdir(parents=True, exist_ok=True)


class FinanceApp(tk.Tk):
    BATCH_SIZE = 200  # Number of rows to load per batch (default 200)
    """Main application window.

    The UI consists of three tabs:
    * **Data** – shows the cleaned CSV in a sortable table.
    * **Statistics** – computes and displays numeric summaries.
    * **Plots** – generates and presents four visualisations.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Finance Analytics")
        self.geometry("1200x800")
        self.style = ttk.Style(self)
        # Use a modern looking theme, fall back to default if unavailable.
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        # Configure comprehensive styles
        self.configure(bg="#f0f2f5")
        self.style.configure("TFrame", background="#f0f2f5")
        # Header
        self.style.configure("Header.TFrame", background="#1a365d")
        self.style.configure("Header.TLabel", background="#1a365d", foreground="white", font=("Helvetica Neue", 18, "bold"))
        # Metric cards
        self.style.configure("MetricCard.TFrame", background="white", relief="solid", borderwidth=1)
        self.style.configure("MetricValue.TLabel", background="white", foreground="#1a365d", font=("Helvetica Neue", 22))
        self.style.configure("MetricLabel.TLabel", background="white", foreground="#718096", font=("Helvetica Neue", 11))
        # Notebook
        self.style.configure("TNotebook", background="#1a365d", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#edf2f7", foreground="#2d3748", padding=[15, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#1a365d")])
        # Action buttons
        self.style.configure("Action.TButton", background="#1a365d", foreground="white", font=("Helvetica Neue", 12, "bold"), padding=[10, 5])
        self.style.map("Action.TButton", background=[("active", "#2b6cb0")])
        # Treeview
        self.style.configure("Treeview", rowheight=32, font=("Menlo", 12), background="white", foreground="#2d3748", fieldbackground="white")
        self.style.configure("Treeview.Heading", background="#1a365d", foreground="white", font=("Helvetica Neue", 13, "bold"), relief="flat")
        self.style.map("Treeview.Heading", background=[("active", "#2b6cb0")])
        # Card LabelFrames
        self.style.configure("Card.TLabelframe", background="white", relief="solid", borderwidth=1)
        self.style.configure("Card.TLabelframe.Label", background="white", foreground="#1a365d", font=("Helvetica Neue", 13, "bold"))
        # Plot card
        self.style.configure("PlotCard.TFrame", background="white", relief="solid", borderwidth=1)
        self.style.configure("PlotCaption.TLabel", background="white", foreground="#718096", font=("Helvetica Neue", 11))
        self._build_header()
        self._create_widgets()
        # Maximize window on start‑up (cross‑platform)
        self._set_initial_window_state()
        # Sorting state: currently sorted column and direction (ascending)
        self._sorted_column: str | None = None
        self._ascending: bool = True
        # Load data once at start‑up.
        self.df: pd.DataFrame | None = None
        self._load_dataset()
        self._populate_data_tab()
        self._update_header_metrics()
        # Statistics will be computed on button click

    # ---------------------------------------------------------------------
    # Header
    # ---------------------------------------------------------------------
    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")
        title = ttk.Label(header, text="◆  Finance Analytics Dashboard", style="Header.TLabel")
        title.pack(side="left", padx=20, pady=15)
        metrics_frame = ttk.Frame(header, style="Header.TFrame")
        metrics_frame.pack(side="right", padx=20, pady=10)
        self._metric_labels: dict[str, ttk.Label] = {}
        for value, label in [
            ("—", "Total Transactions"),
            ("—", "Total Expenses"),
            ("—", "Average Amount"),
            ("—", "Date Range"),
        ]:
            card, val_lbl = self._create_metric_card(metrics_frame, value, label)
            card.pack(side="left", padx=6)
            self._metric_labels[label] = val_lbl

    def _create_metric_card(self, parent: ttk.Frame, value: str, label: str) -> tuple[tk.Frame, ttk.Label]:
        card = tk.Frame(parent, bg="white", relief="solid", bd=1)
        accent = tk.Frame(card, bg="#d69e2e", width=4)
        accent.pack(side="left", fill="y")
        content = tk.Frame(card, bg="white")
        content.pack(side="left", fill="both", expand=True, padx=(12, 18), pady=(6, 6))
        val_lbl = ttk.Label(content, text=value, style="MetricValue.TLabel")
        val_lbl.pack(anchor="w")
        name_lbl = ttk.Label(content, text=label, style="MetricLabel.TLabel")
        name_lbl.pack(anchor="w")
        return card, val_lbl

    def _update_header_metrics(self) -> None:
        if self.df is None:
            return
        total = f"{len(self.df):,}"
        expenses_mask = self.df["transaction_type"] == "Expense"
        expenses_total = self.df.loc[expenses_mask, "amount"].sum()
        expenses_total_str = f"₹{expenses_total:,.0f}" if pd.notna(expenses_total) else "—"
        avg_amount = self.df["amount"].mean()
        avg_str = f"₹{avg_amount:,.2f}" if pd.notna(avg_amount) else "—"
        date_min = self.df["date"].min()
        date_max = self.df["date"].max()
        if pd.notna(date_min):
            date_range_str = f"{date_min.strftime('%b %Y')} – {date_max.strftime('%b %Y')}"
        else:
            date_range_str = "—"
        self._metric_labels["Total Transactions"].config(text=total)
        self._metric_labels["Total Expenses"].config(text=expenses_total_str)
        self._metric_labels["Average Amount"].config(text=avg_str)
        self._metric_labels["Date Range"].config(text=date_range_str)

    # ---------------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------------
    def _create_widgets(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Data tab
        self.data_frame = ttk.Frame(notebook)
        notebook.add(self.data_frame, text="Data")
        self._build_data_tab()

        # Statistics tab
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="Statistics")
        self._build_stats_tab()

        # Plots tab
        self.plots_frame = ttk.Frame(notebook)
        notebook.add(self.plots_frame, text="Plots")
        self._build_plots_tab()

    # ---------------------------------------------------------------------
    # Data tab --------------------------------------------------------------
    # ---------------------------------------------------------------------
    def _build_data_tab(self) -> None:
        # Treeview inside a scrollable frame
        tree_container = ttk.Frame(self.data_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_container, show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        vsb.config(command=self._on_tree_scroll)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        # Zebra striping tags for better readability
        self.tree.tag_configure('odd', background='#f7fafc')
        self.tree.tag_configure('even', background='#ffffff')
        # Button container for Refresh and Load More
        button_frame = ttk.Frame(self.data_frame)
        button_frame.pack(pady=5, anchor='center')

        # Refresh button
        btn = ttk.Button(button_frame, text="Refresh", style="Action.TButton", command=self._refresh_data_tab)
        btn.pack(side='left')

        # Load More button (initially visible)
        self.load_more_btn = ttk.Button(button_frame, text=f"Load more (+{self.BATCH_SIZE})", style="Action.TButton", command=self._load_more_rows)
        self.load_all_btn = ttk.Button(button_frame, text="Load all", style="Action.TButton", command=self._load_all_rows)
        self.load_all_btn.pack(side='left', padx=(5, 0))
        self.load_more_btn.pack(side='left', padx=(5, 0))

    def _load_dataset(self) -> None:
        """Load the cleaned CSV into ``self.df``.
        A simple error dialog is shown if the file cannot be read.
        """
        try:
            self.df = pd.read_csv(CLEANED_DATA_PATH, parse_dates=["date"], keep_default_na=False)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to load dataset: {exc}")
            self.df = None

    def _populate_data_tab(self) -> None:
        # Ensure Load All button visibility based on remaining rows
        if hasattr(self, "load_all_btn"):
            if hasattr(self, "loaded_rows") and self.loaded_rows >= len(self.df):
                self.load_all_btn.pack_forget()
            else:
                if not self.load_all_btn.winfo_ismapped():
                    self.load_all_btn.pack(side='left', padx=(5, 0))
        if self.df is None:
            return
        # Clear existing columns & rows
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)
        for col in self.df.columns:
            # Bind a click on the heading to sort by that column and show sort indicator.
            heading_text = col
            if getattr(self, "_sorted_column", None) == col:
                heading_text += " " + ("▲" if self._ascending else "▼")
            self.tree.heading(
                col,
                text=heading_text,
                command=lambda _col=col: self._sort_by_column(_col),
            )
            anchor = "e" if col == "amount" else "w"
            self.tree.column(col, width=120, anchor=anchor)
        # Determine number of rows to display.
        # If this is the first load or a refresh (loaded_rows not set or 0), show the default batch size.
        if not hasattr(self, "loaded_rows") or self.loaded_rows == 0:
            self.loaded_rows = min(self.BATCH_SIZE, len(self.df))
        else:
            # Preserve the current count (e.g., after loading more rows or sorting)
            self.loaded_rows = min(self.loaded_rows, len(self.df))
        rows = self.df.head(self.loaded_rows).itertuples(index=False, name=None)
        for idx, row in enumerate(rows):
            display_row = []
            for col_name, val in zip(self.df.columns, row):
                if pd.isna(val):
                    display_row.append("")
                elif col_name == "date":
                    display_row.append(val.strftime("%Y-%m-%d"))
                elif col_name == "amount":
                    display_row.append(f"{val:,.2f}")
                else:
                    display_row.append(val)
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", "end", values=display_row, tags=(tag,))
        # Show or hide Load More button based based on remaining rows.
        if self.loaded_rows < len(self.df):
            self._show_load_more_button()
        else:
            self._hide_load_more_button()
    def _sort_by_column(self, col: str) -> None:
        """Sort the DataFrame by *col* and refresh the tree view.

        Toggles between ascending and descending each time the column header is clicked.
        """
        if self.df is None:
            return
        # Determine new sort direction: if this column wasn't previously sorted, start ascending.
        if getattr(self, "_sorted_column", None) != col:
            ascending = True
        else:
            ascending = not self._ascending
        # Update sort state
        self._sorted_column = col
        self._ascending = ascending
        # Perform the sort; use a stable algorithm to preserve relative order when values are equal.
        self.df = self.df.sort_values(by=col, ascending=ascending, kind="mergesort")
        # Keep the current row count after sorting to preserve loaded rows
        # Re‑populate the`` tree with the sorted data.
        self._populate_data_tab()

    def _refresh_data_tab(self) -> None:
        self._load_dataset()
        # Reset sorting state on refresh
        self._sorted_column = None
        self._ascending = True
        self.loaded_rows = 0
        self._populate_data_tab()

    # ---------------------------------------------------------------------
    # Statistics tab --------------------------------------------------------
    # ---------------------------------------------------------------------
    def _load_more_rows(self) -> None:
        """Load the next batch of 200 rows into the Data tab."""
        if self.df is None:
            return
        total_rows = len(self.df)
        if self.loaded_rows >= total_rows:
            self._hide_load_more_button()
            return
        new_end = min(self.loaded_rows + self.BATCH_SIZE, total_rows)
        rows = self.df.iloc[self.loaded_rows:new_end].itertuples(index=False, name=None)
        for offset, row in enumerate(rows):
            idx = self.loaded_rows + offset
            display_row = []
            for col_name, val in zip(self.df.columns, row):
                if pd.isna(val):
                    display_row.append("")
                elif col_name == "date":
                    display_row.append(val.strftime("%Y-%m-%d"))
                elif col_name == "amount":
                    display_row.append(f"{val:,.2f}")
                else:
                    display_row.append(val)
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", "end", values=display_row, tags=(tag,))
        self.loaded_rows = new_end
        if self.loaded_rows >= total_rows:
            self._hide_load_more_button()
        else:
            self._show_load_more_button()
        self.update_idletasks()

    def _load_all_rows(self) -> None:
        """Load the entire dataset into the Data tab."""
        if self.df is None:
            return
        self.loaded_rows = len(self.df)
        self._populate_data_tab()


    def _show_load_more_button(self) -> None:
        if not hasattr(self, "load_more_btn"):
            return
        if not self.load_more_btn.winfo_ismapped():
            self.load_more_btn.pack(side='left', padx=(5, 0))

    def _hide_load_more_button(self) -> None:
        if not hasattr(self, "load_more_btn"):
            return
        if self.load_more_btn.winfo_ismapped():
            self.load_more_btn.pack_forget()

    def _on_tree_scroll(self, *args: str) -> None:
        """Custom scroll handler that forwards to the Treeview and shows Load More when at bottom."""
        self.tree.yview(*args)
        try:
            top, bottom = self.tree.yview()
        except Exception:
            top, bottom = (0.0, 0.0)
        # Keep Load More button visibility based on remaining rows.
        if self.df is not None and self.loaded_rows < len(self.df):
            self._show_load_more_button()
        else:
            self._hide_load_more_button()
    def _build_stats_tab(self) -> None:
        # Container for compute button and scrollable statistics view
        outer_frame = ttk.Frame(self.stats_frame)
        outer_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Compute button at top, centered
        compute_btn = ttk.Button(outer_frame, text="Compute Statistics", style="Action.TButton", command=self._populate_statistics_tab)
        compute_btn.pack(pady=10)

        # Scrollable canvas for statistics sections
        canvas = tk.Canvas(outer_frame, bg="#f0f2f5", highlightthickness=0)
        vscroll = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame inside canvas that will hold the stats widgets
        self.stats_container = ttk.Frame(canvas)
        self.stats_canvas_window = canvas.create_window((0, 0), window=self.stats_container, anchor="nw")
        # Update scroll region when size changes
        self.stats_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # Ensure inner frame expands to canvas width
        def _on_stats_canvas_configure(event):
            canvas.itemconfig(self.stats_canvas_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", _on_stats_canvas_configure)

    def _populate_statistics_tab(self) -> None:
        """Compute statistics and display them in a structured GUI."""
        # Clear any existing widgets in the stats container
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        if not CLEANED_DATA_PATH.exists():
            msg = ttk.Label(self.stats_container, text="Cleaned dataset not found.")
            msg.pack(pady=5)
            return
        try:
            amounts, dates_int = load_amounts_and_dates(str(CLEANED_DATA_PATH))
            basic = compute_basic_stats(amounts)
            corr_trend = compute_correlation_and_trend(amounts, dates_int)
            categories, counts = frequency_distribution(str(CLEANED_DATA_PATH), column_index=4)
        except Exception as exc:
            err = ttk.Label(self.stats_container, text=f"Error while computing statistics: {exc}")
            err.pack(pady=5)
            return

        self._update_header_metrics()

        # ----- Basic Statistics -----
        basic_frame = ttk.LabelFrame(self.stats_container, text="Basic Statistics", style="Card.TLabelframe")
        basic_frame.pack(fill="x", padx=12, pady=8)
        body_font = ("Helvetica Neue", 12)
        mono_font = ("Menlo", 12)
        for i, (k, v) in enumerate(basic.items()):
            ttk.Label(basic_frame, text=f"{k.title()}: ", font=body_font).grid(row=i, column=0, sticky="w", padx=(14, 5), pady=3)
            ttk.Label(basic_frame, text=f"{v:.4f}", font=mono_font).grid(row=i, column=1, sticky="e", padx=(5, 14), pady=3)

        # ----- Correlation & Trend -----
        corr_frame = ttk.LabelFrame(self.stats_container, text="Correlation & Trend", style="Card.TLabelframe")
        corr_frame.pack(fill="x", padx=12, pady=8)
        from computations.compute_stats import forecast_next_amount
        forecast = forecast_next_amount(corr_trend, dates_int.max(), days_ahead=30)
        corr_items = [
            ("Pearson correlation", corr_trend["correlation"]),
            ("Slope", corr_trend["slope"]),
            ("Intercept", corr_trend["intercept"]),
            ("R‑value", corr_trend["r_value"]),
            ("P‑value", corr_trend["p_value"]),
            ("Forecast (30 days)", forecast),
        ]
        for i, (label, value) in enumerate(corr_items):
            ttk.Label(corr_frame, text=f"{label}: ", font=body_font).grid(row=i, column=0, sticky="w", padx=(14, 5), pady=3)
            ttk.Label(corr_frame, text=f"{value:.4f}", font=mono_font).grid(row=i, column=1, sticky="e", padx=(5, 14), pady=3)

        # ----- Category Frequency -----
        freq_frame = ttk.LabelFrame(self.stats_container, text="Category Frequency", style="Card.TLabelframe")
        freq_frame.pack(fill="both", expand=True, padx=12, pady=8)

        tree = ttk.Treeview(freq_frame, columns=("Category", "Count"), show="headings", height=10)
        tree.heading("Category", text="Category")
        tree.heading("Count", text="Count")
        tree.column("Category", anchor="w")
        tree.column("Count", anchor="center")
        vsb = ttk.Scrollbar(freq_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for cat, cnt in zip(categories, counts):
            tree.insert("", "end", values=(cat, cnt))

    # ---------------------------------------------------------------------
    # Plots tab -------------------------------------------------------------
    # ---------------------------------------------------------------------
    def _build_plots_tab(self) -> None:
        # Container for generate button and scrollable images view
        outer_frame = ttk.Frame(self.plots_frame)
        outer_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Generate button at top, centered
        gen_btn = ttk.Button(outer_frame, text="Generate Plots", style="Action.TButton", command=self._generate_plots)
        gen_btn.pack(pady=10)

        # Scrollable canvas for images
        canvas_frame = ttk.Frame(outer_frame)
        canvas_frame.pack(fill="both", expand=True, padx=0, pady=10)
        self.canvas = tk.Canvas(canvas_frame, bg="#f0f2f5", highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        # Frame inside canvas
        self.plots_container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.plots_container, anchor="nw")
        self.plots_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind("<Configure>", _on_canvas_configure)
        # Ensure canvas gets focus on hover and bind mouse wheel scrolling.
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        self.canvas.bind_all("<MouseWheel>", self._on_canvas_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_canvas_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_canvas_mousewheel_linux)


    def _generate_plots(self) -> None:
        """Invoke visualisation helpers to (re)create PNG charts and display them.
        """
        # Ensure we have data.
        if self.df is None:
            messagebox.showerror("Error", "Dataset not loaded – cannot generate plots.")
            return
        # Use the helper functions – they will overwrite existing PNGs.
        try:
            bar_expenses_by_category(self.df)
            line_monthly_expense_trend(self.df)
            pie_payment_mode_distribution(self.df)
            histogram_expense_amount(self.df)
        except Exception as exc:
            messagebox.showerror("Plot Error", f"Failed to generate plots: {exc}")
            return
        # Load generated images.
        self._display_plot_images()
        messagebox.showinfo("Success", f"Plots saved to {VIS_IMG_DIR}")

    def _display_plot_images(self) -> None:
        """Load generated PNGs, resize them to fit within the window, and display."""
        # Clear previous images.
        for widget in self.plots_container.winfo_children():
            widget.destroy()
        # Load each PNG in sorted order for consistency.
        png_paths = sorted(VIS_IMG_DIR.glob("*.png"))
        for path in png_paths:
            try:
                # Use Pillow to resize if available, otherwise fallback to Tkinter PhotoImage.
                if Image and ImageTk:
                    pil_img = Image.open(path)
                    # Set a max size that fits the application window (e.g., 800x600).
                    max_width, max_height = 800, 600
                    # Choose appropriate resampling filter for Pillow version compatibility.
                    resample = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", None))
                    if resample is not None:
                        pil_img.thumbnail((max_width, max_height), resample)
                    else:
                        pil_img.thumbnail((max_width, max_height))
                    img = ImageTk.PhotoImage(pil_img)
                else:
                    img = tk.PhotoImage(file=str(path))
            except Exception:
                # Skip unreadable or unsupported image files.
                continue
            card = ttk.Frame(self.plots_container, style="PlotCard.TFrame")
            card.pack(pady=10, padx=24, fill="x")
            lbl = ttk.Label(card, image=img, background="white")
            lbl.image = img
            lbl.pack(pady=(10, 5), padx=10)
            caption = ttk.Label(card, text=path.stem.replace("_", " ").title(), style="PlotCaption.TLabel")
            caption.pack(pady=(0, 10))
        # Force geometry update so scrollregion reflects new content
        self.canvas.update_idletasks()

    def _on_canvas_mousewheel(self, event):
        """Handle mouse wheel events for Windows and macOS platforms.
        Supports both Windows (delta multiples of 120) and macOS (small delta values).
        """
        # Determine scroll amount based on event.delta magnitude.
        if event.delta:
            # On Windows, delta is usually a multiple of 120.
            # On macOS, delta is often a small integer (1 or -1).
            if abs(event.delta) >= 120:
                delta = int(-1 * (event.delta / 120))
            else:
                delta = int(-1 * event.delta)
            self.canvas.yview_scroll(delta, "units")
        return "break"

    def _on_canvas_mousewheel_linux(self, event):
        """Handle mouse wheel events for Linux platforms (Button-4/5)."""
        # ``event.num`` indicates which button was pressed: 4 = scroll up, 5 = scroll down.
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        return "break"

    def _set_initial_window_state(self) -> None:
        """Maximize the window on start‑up, handling cross‑platform differences.

        - Windows: uses ``self.state('zoomed')``.
        - macOS / Linux: falls back to setting the geometry to the screen size.
        """
        try:
            # Windows maximize
            self.state("zoomed")
        except tk.TclError:
            # Fallback for macOS / Linux
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}")


def main() -> None:
    app = FinanceApp()
    app.mainloop()

if __name__ == "__main__":
    main()
