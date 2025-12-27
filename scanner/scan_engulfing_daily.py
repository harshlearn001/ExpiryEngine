#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Daily Engulfing Candle Scanner (EOD)

✔ Bullish & Bearish Engulfing
✔ Day-close only
✔ No trend filter
✔ Pure price action
✔ Production safe
"""

from pathlib import Path
import pandas as pd

# ==================================================
# PATHS
# ==================================================
BASE = Path(r"H:\ExpiryEngine")
DATA_DIR = BASE / "data" / "master"
OUT_DIR = BASE / "data" / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "engulfing_daily.csv"

# ==================================================
# HELPERS
# ==================================================
def normalize_cols(df):
    df.columns = (
        df.columns
        .str.strip()
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

        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df.sort_values("DATE").reset_index(drop=True)

        if len(df) < 2:
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        po, pc = prev["OPEN"], prev["CLOSE"]
        co, cc = curr["OPEN"], curr["CLOSE"]

        # Candle direction
        prev_red = pc < po
        prev_green = pc > po
        curr_green = cc > co
        curr_red = cc < co

        # Body ranges
        prev_body_low = min(po, pc)
        prev_body_high = max(po, pc)

        curr_body_low = min(co, cc)
        curr_body_high = max(co, cc)

        # ==================================================
        # BULLISH ENGULFING
        # ==================================================
        if (
            prev_red and
            curr_green and
            curr_body_low <= prev_body_low and
            curr_body_high >= prev_body_high
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

        # ==================================================
        # BEARISH ENGULFING
        # ==================================================
        if (
            prev_green and
            curr_red and
            curr_body_low <= prev_body_low and
            curr_body_high >= prev_body_high
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
        print(f"⚠️ Skipped {symbol}: {e}")

# ==================================================
# SAVE
# ==================================================
if rows:
    out_df = pd.DataFrame(rows).sort_values(["TYPE", "SYMBOL"])
    out_df.to_csv(OUT_FILE, index=False)
    print(f"✅ Engulfing candles found: {len(out_df)}")
    print(f"📁 Output: {OUT_FILE}")
else:
    print("ℹ️ No Engulfing candle found today")
