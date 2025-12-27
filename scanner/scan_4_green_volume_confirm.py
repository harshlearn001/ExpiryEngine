#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Daily Scanner (NSE Master CSV):
✔ Last 4 trading days GREEN candles
✔ Day-4 volume is highest in last 4 days
"""

from pathlib import Path
import pandas as pd

# ================= PATHS =================
DATA_DIR = Path(r"H:\ExpiryEngine\data\master")
OUT_DIR = Path(r"H:\ExpiryEngine\data\reports\green_4_volume_confirm")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "scan_4_green_volume_confirm.csv"

CANDLE_COUNT = 4

# ================= LOGIC =================
def is_green(row):
    return row["close"] > row["open"]

def volume_confirm(vols):
    return vols[-1] == max(vols)

# ================= MAIN =================
def main():
    results = []

    files = sorted(DATA_DIR.glob("*.csv"))
    print(f"🔍 Scanning {len(files)} symbols (DAILY)...\n")

    for file in files:
        symbol = file.stem
        df = pd.read_csv(file)

        # Normalize NSE columns
        df.columns = df.columns.str.strip().str.lower()

        required = {"open", "close", "tottrdqty"}
        if not required.issubset(df.columns):
            continue

        if len(df) < CANDLE_COUNT:
            continue

        last = df.tail(CANDLE_COUNT)

        # 1️⃣ All green candles
        if not all(last.apply(is_green, axis=1)):
            continue

        # 2️⃣ Volume confirmation on Day-4
        volumes = last["tottrdqty"].tolist()
        if not volume_confirm(volumes):
            continue

        results.append({
            "SYMBOL": symbol,
            "VOL_D4": volumes[-1],
            "CLOSE_D4": last.iloc[-1]["close"],
        })

        print(f"✓ {symbol}")

    if results:
        pd.DataFrame(results).to_csv(OUT_FILE, index=False)
        print(f"\n✅ Scan completed → {OUT_FILE}")
    else:
        print("\n⚠ No symbols matched")

if __name__ == "__main__":
    main()
