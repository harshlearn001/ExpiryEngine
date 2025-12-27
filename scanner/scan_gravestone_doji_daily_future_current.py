#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Futures Gravestone Doji Scanner (EOD)

✔ Futures data (multi-expiry safe)
✔ Selects NEAREST (front-month) expiry
✔ No trend filter
✔ Day-close only
✔ Pure candle anatomy
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

OUT_FILE = OUT_DIR / "gravestone_doji_daily_future_current.csv"

# ==================================================
# PARAMETERS
# ==================================================
BODY_PCT_MAX = 0.2
LOWER_WICK_MAX = 0.2
UPPER_WICK_MIN = 0.6

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

        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE", "EXPIRY"}
        if not required.issubset(df.columns):
            continue

        # ----------------------------------
        # NORMALIZE DATES
        # ----------------------------------
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["EXPIRY"] = pd.to_datetime(df["EXPIRY"])

        # ----------------------------------
        # FIND LAST TRADING DATE
        # ----------------------------------
        last_trade_date = df["DATE"].max()

        # ----------------------------------
        # SELECT NEAREST (FRONT) EXPIRY
        # ----------------------------------
        valid_expiries = df.loc[df["EXPIRY"] >= last_trade_date, "EXPIRY"]
        if valid_expiries.empty:
            continue

        front_expiry = valid_expiries.min()
        df = df[df["EXPIRY"] == front_expiry]

        # ----------------------------------
        # SORT BY DATE
        # ----------------------------------
        df = df.sort_values("DATE").reset_index(drop=True)
        last = df.iloc[-1]

        # ----------------------------------
        # CANDLE VALUES
        # ----------------------------------
        o, h, l, c = last["OPEN"], last["HIGH"], last["LOW"], last["CLOSE"]
        rng = h - l
        if rng <= 0:
            continue

        body = abs(o - c)
        upper = h - max(o, c)
        lower = min(o, c) - l

        # ----------------------------------
        # GRAVESTONE DOJI CHECK
        # ----------------------------------
        if (
            body <= BODY_PCT_MAX * rng and
            lower <= LOWER_WICK_MAX * rng and
            upper >= UPPER_WICK_MIN * rng
        ):
            rows.append({
                "SYMBOL": symbol,
                "EXPIRY": front_expiry.date(),
                "DATE": last["DATE"].date(),
                "OPEN": o,
                "HIGH": h,
                "LOW": l,
                "CLOSE": c,
                "UPPER_WICK_%": round(upper / rng * 100, 2),
                "BODY_%": round(body / rng * 100, 2),
                "LOWER_WICK_%": round(lower / rng * 100, 2)
            })

    except Exception as e:
        print(f"⚠️ {symbol} skipped: {e}")

# ==================================================
# SAVE
# ==================================================
if rows:
    out = pd.DataFrame(rows).sort_values("UPPER_WICK_%", ascending=False)
    out.to_csv(OUT_FILE, index=False)
    print(f"✅ Futures Gravestone Doji found: {len(out)}")
    print(f"📁 Output: {OUT_FILE}")
else:
    print("ℹ️ No Futures Gravestone Doji found today")
