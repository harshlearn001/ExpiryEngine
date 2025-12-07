"""
view_candles.py

Usage examples (from project root H:\ExpiryEngine):
    # View RELIANCE weekly (full history)
    python view_candles.py --file data/weekly/RELIANCE.csv --title "RELIANCE Weekly"

    # View RELIANCE weekly (last 5 years)
    python view_candles.py --file data/weekly/RELIANCE.csv --years 5 --title "RELIANCE Weekly (5y)"

    # Save to a custom file
    python view_candles.py --file data/weekly/RELIANCE.csv --out out/reliance_weekly.png
"""

import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def normalize_columns(df):
    """Map common lowercase/uppercase headers to Date/Open/High/Low/Close."""
    col_map = {
        "date": "Date",
        "week_start": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "close_price": "Close",
    }
    # unify by lowercasing existing columns for matching
    rename_map = {}
    for c in df.columns:
        lc = c.strip().lower()
        if lc in col_map:
            rename_map[c] = col_map[lc]
    return df.rename(columns=rename_map)


def load_df(path):
    df = pd.read_csv(path)
    df = normalize_columns(df)

    if "Date" not in df.columns:
        raise ValueError("No 'Date' column found after normalization. File headers: " + ", ".join(df.columns))

    # ensure OHLC exist
    required = {"Open", "High", "Low", "Close"}
    if not required.issubset(df.columns):
        raise ValueError("Missing OHLC columns. Found: " + ", ".join(df.columns))

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def plot_candles(df, title="Candlestick Chart", last_n_years=None, save_path=None,
                 wick_lw=0.8, body_width=0.7, body_linewidth=1.2):
    # Crop to last_n_years if requested
    if last_n_years is not None:
        last_date = df["Date"].max()
        cutoff = last_date - pd.DateOffset(years=last_n_years)
        df = df[df["Date"] >= cutoff].reset_index(drop=True)

    # numeric x positions for even spacing (TradingView style)
    df = df.reset_index(drop=True)
    df["x"] = df.index.astype(float)

    fig, ax = plt.subplots(figsize=(14, 7))

    for _, r in df.iterrows():
        x = r["x"]
        o = float(r["Open"])
        h = float(r["High"])
        l = float(r["Low"])
        c = float(r["Close"])

        color = "#26A69A" if c >= o else "#EF5350"  # green/red similar to TV
        # thin wick
        ax.plot([x, x], [l, h], color=color, linewidth=wick_lw, zorder=2)
        # body
        height = abs(c - o)
        bottom = min(o, c)
        rect = Rectangle((x - body_width/2, bottom), body_width, height,
                         facecolor=color, edgecolor=color, linewidth=body_linewidth, zorder=3)
        ax.add_patch(rect)

    # Format x axis with readable date ticks
    n = len(df)
    if n == 0:
        raise ValueError("No data to plot after filtering.")
    tick_step = max(1, n // 12)  # about 12 ticks along x
    ticks = df["x"].tolist()[::tick_step]
    labels = df["Date"].dt.strftime("%Y-%m-%d").tolist()[::tick_step]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, ha="right")

    # Visual style - TradingView white/theme
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.25)

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=300)
        print("Saved chart to:", save_path)

    plt.show()


def main():
    parser = argparse.ArgumentParser(description="View candlestick chart from CSV (weekly/monthly/daily).")
    parser.add_argument("--file", "-f", required=True, help="CSV file path (e.g. data/weekly/RELIANCE.csv)")
    parser.add_argument("--years", "-y", type=int, default=None, dest="last_n_years",
                        help="Plot only the last N years (optional).")
    parser.add_argument("--title", "-t", default=None, help="Chart title.")
    parser.add_argument("--out", "-o", default=None, help="Save chart to this PNG path (optional).")
    args = parser.parse_args()

    df = load_df(args.file)
    title = args.title or os.path.basename(args.file).replace(".csv", "")
    plot_candles(df, title=title, last_n_years=args.last_n_years, save_path=args.out)


if __name__ == "__main__":
    main()
