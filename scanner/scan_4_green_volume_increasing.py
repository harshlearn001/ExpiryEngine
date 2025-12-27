#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Daily Scanner (NSE Master CSV):
✔ Last 4 trading days GREEN candles
✔ Volume strictly increasing (TOTTRDQTY)
"""

from pathlib import Path
import pandas as pd

# ================= PATHS =================
DATA_DIR = Path(r"H:\ExpiryEngine\data\master")
OUT_DIR = Path(r"H:\ExpiryEngine\data\reports\green_4_volume_inc")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "scan_4_green_volume_increasing.csv"

CANDLE_COUNT = 4

# ================= LOGIC =================
def is_green(row):
    return row["close"] > row["open"]

def volume_increasing(vols):
    return vols[0] < vols[1] < vols[2] < vols[3]

# ================= MAIN =================
def main():
    results = []

    files = sorted(DATA_DIR.glob("*.csv"))
    print(f"🔍 Scanning {len(files)} symbols (DAILY)...\n")

    for file in files:
        symbol = file.stem

        df = pd.read_csv(file)

        # ---- Normalize columns (NSE MASTER SAFE) ----
        df.columns = (
            df.columns
              .str.strip()
              .str.lower()
        )

        required = {"open", "close", "tottrdqty"}
        if not required.issubset(df.columns):
            print(f"⚠ Skipped {symbol} (missing NSE columns)")
            continue

        if len(df) < CANDLE_COUNT:
            continue

        last = df.tail(CANDLE_COUNT)

        # 1️⃣ All candles green
        if not all(last.apply(is_green, axis=1)):
            continue

        # 2️⃣ Volume strictly increasing
        volumes = last["tottrdqty"].tolist()
        if not volume_increasing(volumes):
            continue

        results.append({
            "SYMBOL": symbol,
            "VOL_D1": volumes[0],
            "VOL_D2": volumes[1],
            "VOL_D3": volumes[2],
            "VOL_D4": volumes[3],
            "CLOSE_D4": last.iloc[-1]["close"],
        })

        print(f"✓ {symbol}")

    # ================= OUTPUT =================
    if results:
        pd.DataFrame(results).to_csv(OUT_FILE, index=False)
        print(f"\n✅ Scan completed → {OUT_FILE}")
    else:
        print("\n⚠ No symbols matched")

if __name__ == "__main__":
    main()
