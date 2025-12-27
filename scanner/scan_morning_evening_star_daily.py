#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Morning Star & Evening Star Scanner (EOD)

✔ Equity (cash) data
✔ Day-close only
✔ No trend filter
✔ Pure 3-candle structure
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

OUT_FILE = OUT_DIR / "morning_evening_star_daily.csv"

# ==================================================
# PARAMETERS
# ==================================================
STRONG_BODY_MIN = 0.6   # candle body >= 60% of range
SMALL_BODY_MAX = 0.3   # candle body <= 30% of range

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


def candle_parts(row):
    o, h, l, c = row["OPEN"], row["HIGH"], row["LOW"], row["CLOSE"]
    rng = h - l
    body = abs(o - c)
    return rng, body


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

        if len(df) < 3:
            continue

        c1 = df.iloc[-3]
        c2 = df.iloc[-2]
        c3 = df.iloc[-1]

        r1, b1 = candle_parts(c1)
        r2, b2 = candle_parts(c2)
        r3, b3 = candle_parts(c3)

        if min(r1, r2, r3) <= 0:
            continue

        # Candle directions
        c1_red = c1["CLOSE"] < c1["OPEN"]
        c1_green = c1["CLOSE"] > c1["OPEN"]
        c3_green = c3["CLOSE"] > c3["OPEN"]
        c3_red = c3["CLOSE"] < c3["OPEN"]

        # Strength
        c1_strong = b1 >= STRONG_BODY_MIN * r1
        c2_small = b2 <= SMALL_BODY_MAX * r2
        c3_strong = b3 >= STRONG_BODY_MIN * r3

        # ==================================================
        # MORNING STAR
        # ==================================================
        if (
            c1_red and
            c1_strong and
            c2_small and
            c3_green and
            c3_strong and
            c3["CLOSE"] >= (c1["OPEN"] + c1["CLOSE"]) / 2
        ):
            rows.append({
                "SYMBOL": symbol,
                "DATE": c3["DATE"].date(),
                "PATTERN": "MORNING_STAR",
                "C1_DATE": c1["DATE"].date(),
                "C2_DATE": c2["DATE"].date(),
                "C3_DATE": c3["DATE"].date()
            })

        # ==================================================
        # EVENING STAR
        # ==================================================
        if (
            c1_green and
            c1_strong and
            c2_small and
            c3_red and
            c3_strong and
            c3["CLOSE"] <= (c1["OPEN"] + c1["CLOSE"]) / 2
        ):
            rows.append({
                "SYMBOL": symbol,
                "DATE": c3["DATE"].date(),
                "PATTERN": "EVENING_STAR",
                "C1_DATE": c1["DATE"].date(),
                "C2_DATE": c2["DATE"].date(),
                "C3_DATE": c3["DATE"].date()
            })

    except Exception as e:
        print(f"⚠️ {symbol} skipped: {e}")

# ==================================================
# SAVE
# ==================================================
if rows:
    out_df = pd.DataFrame(rows).sort_values(["PATTERN", "SYMBOL"])
    out_df.to_csv(OUT_FILE, index=False)
    print(f"✅ Morning / Evening Star found: {len(out_df)}")
    print(f"📁 Output: {OUT_FILE}")
else:
    print("ℹ️ No Morning or Evening Star found today")
