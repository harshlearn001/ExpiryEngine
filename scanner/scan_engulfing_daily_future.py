#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Futures Engulfing Candle Scanner (EOD)

✔ Bullish & Bearish
✔ Futures data
✔ No trend filter
✔ Day-close only
"""

from pathlib import Path
import pandas as pd

# ==================================================
# PATHS
# ==================================================
BASE = Path(r"H:\ExpiryEngine")
DATA_DIR = BASE / "data" / "master_future"
OUT_DIR = BASE / "data" / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "engulfing_daily_future.csv"

# ==================================================
# HELPERS
# ==================================================
def normalize_cols(df):
    df.columns = (
        df.columns.str.strip()
                  .str.upper()
                  .str.replace("*", "", regex=False)
    )
    return df

# ==================================================
# SCAN
# ==================================================
rows = []

for csv_file in sorted(DATA_DIR.glob("*.csv")):
    symbol = csv_file.stem

    try:
        df = pd.read_csv(csv_file)
        df = normalize_cols(df)

        req = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not req.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df.sort_values("DATE").reset_index(drop=True)

        if len(df) < 2:
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        po, pc = prev["OPEN"], prev["CLOSE"]
        co, cc = curr["OPEN"], curr["CLOSE"]

        prev_red = pc < po
        prev_green = pc > po
        curr_green = cc > co
        curr_red = cc < co

        prev_low = min(po, pc)
        prev_high = max(po, pc)
        curr_low = min(co, cc)
        curr_high = max(co, cc)

        # Bullish engulfing
        if (
            prev_red and curr_green and
            curr_low <= prev_low and
            curr_high >= prev_high
        ):
            rows.append({
                "SYMBOL": symbol,
                "DATE": curr["DATE"].date(),
                "TYPE": "BULLISH",
                "OPEN": co,
                "HIGH": curr["HIGH"],
                "LOW": curr["LOW"],
                "CLOSE": cc
            })

        # Bearish engulfing
        if (
            prev_green and curr_red and
            curr_low <= prev_low and
            curr_high >= prev_high
        ):
            rows.append({
                "SYMBOL": symbol,
                "DATE": curr["DATE"].date(),
                "TYPE": "BEARISH",
                "OPEN": co,
                "HIGH": curr["HIGH"],
                "LOW": curr["LOW"],
                "CLOSE": cc
            })

    except Exception as e:
        print(f"⚠️ {symbol} skipped: {e}")

# ==================================================
# SAVE
# ==================================================
if rows:
    out = pd.DataFrame(rows).sort_values(["TYPE", "SYMBOL"])
    out.to_csv(OUT_FILE, index=False)
    print(f"✅ Futures Engulfing candles found: {len(out)}")
    print(f"📁 Output: {OUT_FILE}")
else:
    print("ℹ️ No Futures Engulfing candle found today")
