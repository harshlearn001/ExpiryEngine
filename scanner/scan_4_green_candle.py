#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Daily Scanner:
✔ Last 4 trading days are GREEN candles
(NSE master CSV safe)
"""

from pathlib import Path
import pandas as pd

# ================= PATHS =================
DATA_DIR = Path(r"H:\ExpiryEngine\data\master")
OUT_DIR = Path(r"H:\ExpiryEngine\data\reports\green_candle_4_day")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "scan_last_4_green_daily.csv"

CANDLE_COUNT = 4

# ================= LOGIC =================
def is_green(row):
    return row["CLOSE"] > row["OPEN"]

# ================= MAIN =================
def main():
    results = []

    files = sorted(DATA_DIR.glob("*.csv"))
    print(f"🔍 Scanning {len(files)} symbols (DAILY)...\n")

    for file in files:
        symbol = file.stem

        df = pd.read_csv(file)

        # ---- Normalize column names (CRITICAL) ----
        df.columns = (
            df.columns
              .str.strip()
              .str.upper()
        )

        # ---- Column safety check ----
        required = {"OPEN", "CLOSE"}
        if not required.issubset(df.columns):
            print(f"⚠ Skipped {symbol} (missing OPEN/CLOSE)")
            continue

        if len(df) < CANDLE_COUNT:
            continue

        last = df.tail(CANDLE_COUNT)

        # ---- All 4 days must be green ----
        if not all(last.apply(is_green, axis=1)):
            continue

        results.append({
            "SYMBOL": symbol,
            "D1_OPEN": last.iloc[0]["OPEN"],
            "D1_CLOSE": last.iloc[0]["CLOSE"],
            "D4_CLOSE": last.iloc[-1]["CLOSE"],
        })

        print(f"✓ {symbol}")

    # ================= OUTPUT =================
    if results:
        out_df = pd.DataFrame(results)
        out_df.to_csv(OUT_FILE, index=False)
        print(f"\n✅ Scan completed → {OUT_FILE}")
    else:
        print("\n⚠ No symbols matched")

if __name__ == "__main__":
    main()
