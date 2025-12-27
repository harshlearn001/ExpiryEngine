#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine | Futures Gravestone Doji Scanner (EOD)

✔ Scans TOP 3 expiries per symbol
✔ Each expiry scanned independently
✔ Outputs expiry-wise CSV files
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
OUT_BASE = BASE / "data" / "reports" / "gravestone_doji_future_3expiry"
OUT_BASE.mkdir(parents=True, exist_ok=True)

# ==================================================
# PARAMETERS
# ==================================================
BODY_PCT_MAX = 0.2
LOWER_WICK_MAX = 0.2
UPPER_WICK_MIN = 0.6
MAX_EXPIRIES = 3   # <<< KEY CHANGE

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
# STORAGE (expiry-wise)
# ==================================================
expiry_rows = {}  # {expiry_date: [rows...]}

# ==================================================
# SCAN
# ==================================================
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

        last_trade_date = df["DATE"].max()

        # ----------------------------------
        # SELECT ACTIVE EXPIRIES (NEAREST FIRST)
        # ----------------------------------
        expiries = (
            df.loc[df["EXPIRY"] >= last_trade_date, "EXPIRY"]
              .drop_duplicates()
              .sort_values()
              .head(MAX_EXPIRIES)
        )

        for expiry in expiries:
            sub = df[df["EXPIRY"] == expiry].sort_values("DATE")

            if len(sub) < 1:
                continue

            last = sub.iloc[-1]

            o, h, l, c = last["OPEN"], last["HIGH"], last["LOW"], last["CLOSE"]
            rng = h - l
            if rng <= 0:
                continue

            body = abs(o - c)
            upper = h - max(o, c)
            lower = min(o, c) - l

            if (
                body <= BODY_PCT_MAX * rng and
                lower <= LOWER_WICK_MAX * rng and
                upper >= UPPER_WICK_MIN * rng
            ):
                expiry_rows.setdefault(expiry.date(), []).append({
                    "SYMBOL": symbol,
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
# SAVE EXPIRY-WISE FILES
# ==================================================
if not expiry_rows:
    print("ℹ️ No Futures Gravestone Doji found today")
else:
    for expiry, rows in expiry_rows.items():
        out_file = OUT_BASE / f"gravestone_doji_{expiry}.csv"
        df_out = pd.DataFrame(rows).sort_values("UPPER_WICK_%", ascending=False)
        df_out.to_csv(out_file, index=False)
        print(f"✅ {expiry} → {len(df_out)} signals | {out_file}")
