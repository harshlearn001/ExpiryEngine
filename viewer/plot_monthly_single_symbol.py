#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Plot MONTHLY candles for ONE symbol
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
def plot_candles(df, symbol):
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
    plt.show()

# ================= MAIN =================
def main():
    symbol = input("Enter SYMBOL (e.g. RELIANCE): ").strip().upper()
    candle_count = int(
        input("How many LAST monthly candles to plot (2 / 3 / 6 / 12 / N): ")
    )

    file = MONTHLY_DIR / f"{symbol}.csv"

    if not file.exists():
        print("❌ Symbol file not found")
        return

    df = pd.read_csv(file)

    if df.empty:
        print("❌ Empty CSV file")
        return

    df_view = df.tail(candle_count).reset_index(drop=True)

    plot_candles(df_view, symbol)

    # Save also
    out_file = OUT_DIR / f"{symbol}_last_{candle_count}.png"
    plt.savefig(out_file)
    plt.close()

    print(f"✓ Chart saved: {out_file}")

if __name__ == "__main__":
    main()
