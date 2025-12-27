#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Plot MONTHLY candles for ALL symbols
Manual candle count
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ================= PATHS =================
MONTHLY_DIR = Path(r"H:\ExpiryEngine\data\monthly_candle_data")
OUT_DIR = Path(r"H:\ExpiryEngine\data\monthly_charts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ================= PLOT =================
def plot_candles(df, symbol, out_file):
    plt.figure(figsize=(10, 5))

    for i, row in df.iterrows():
        color = "green" if row["Close"] >= row["Open"] else "red"

        # Wick
        plt.plot(
            [i, i],
            [row["Low"], row["High"]],
            color="black",
            linewidth=1
        )

        # Body
        plt.bar(
            i,
            row["Close"] - row["Open"],
            bottom=row["Open"],
            color=color,
            width=0.6
        )

    plt.title(f"{symbol} | Monthly")
    plt.xlabel("Candles")
    plt.ylabel("Price")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()

# ================= MAIN =================
def main():
    candle_count = int(
        input("How many LAST monthly candles to plot (2 / 3 / 4 / 6 / 12 / N): ")
    )

    files = sorted(MONTHLY_DIR.glob("*.csv"))
    print(f"\nProcessing {len(files)} symbols...\n")

    for file in files:
        symbol = file.stem
        df = pd.read_csv(file)

        if df.empty:
            continue

        df_view = df.tail(candle_count)

        out_file = OUT_DIR / f"{symbol}_last_{candle_count}.png"
        plot_candles(df_view.reset_index(drop=True), symbol, out_file)

        print(f"✓ {symbol}")

    print("\n✅ ALL SYMBOL MONTHLY CHARTS CREATED")

if __name__ == "__main__":
    main()
