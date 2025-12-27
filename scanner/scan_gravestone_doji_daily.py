#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Pure Gravestone Doji Scanner (EOD)

✔ No trend filter
✔ Day-close only
✔ Strict candle anatomy
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

OUT_FILE = OUT_DIR / "gravestone_doji_daily.csv"

# ==================================================
# PARAMETERS (PURE CANDLE)
# ==================================================
BODY_PCT_MAX = 0.2       # body <= 20% of range
LOWER_WICK_MAX = 0.2    # lower wick <= 20% of range
UPPER_WICK_MIN = 0.6    # upper wick >= 60% of range

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

        if len(df) < 1:
            continue

        last = df.iloc[-1]

        o, h, l, c = last["OPEN"], last["HIGH"], last["LOW"], last["CLOSE"]
        rng = h - l

        if rng <= 0:
            continue

        body = abs(o - c)
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l

        # ----------------------------------
        # PURE GRAVESTONE CHECK
        # ----------------------------------
        if (
            body <= BODY_PCT_MAX * rng and
            lower_wick <= LOWER_WICK_MAX * rng and
            upper_wick >= UPPER_WICK_MIN * rng
        ):
            rows.append({
                "SYMBOL": symbol,
                "DATE": last["DATE"].date(),
                "OPEN": o,
                "HIGH": h,
                "LOW": l,
                "CLOSE": c,
                "UPPER_WICK_%": round(upper_wick / rng * 100, 2),
                "BODY_%": round(body / rng * 100, 2),
                "LOWER_WICK_%": round(lower_wick / rng * 100, 2)
            })

    except Exception as e:
        print(f"⚠️ Skipped {symbol}: {e}")

# ==================================================
# SAVE
# ==================================================
if rows:
    out_df = pd.DataFrame(rows).sort_values("UPPER_WICK_%", ascending=False)
    out_df.to_csv(OUT_FILE, index=False)
    print(f"✅ Gravestone Doji found: {len(out_df)}")
    print(f"📁 Output: {OUT_FILE}")
else:
    print("ℹ️ No Gravestone Doji found today")
