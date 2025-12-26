#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Build MONTHLY candles
Month = First Wednesday → Last Tuesday
"""

import pandas as pd
from pathlib import Path

# ================= PATHS =================
MASTER_DIR = Path(r"H:\ExpiryEngine\data\master")
OUT_DIR = Path(r"H:\ExpiryEngine\data\monthly_candle_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ================= LOGIC =================
def build_monthly(df):
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Monday=0 ... Wednesday=2
    df["weekday"] = df["date"].dt.weekday

    # First Wednesday of month
    df["is_first_wed"] = (
        (df["weekday"] == 2) &
        (df["date"].dt.day <= 7)
    )

    # New month group on first Wednesday
    df["month_id"] = df["is_first_wed"].cumsum()

    monthly = (
        df.groupby("month_id")
        .agg(
            Month_Start=("date", "min"),
            Month_End=("date", "max"),
            Open=("open", "first"),
            High=("high", "max"),
            Low=("low", "min"),
            Close=("close", "last"),
        )
        .reset_index(drop=True)
    )

    return monthly

# ================= MAIN =================
def main():
    files = sorted(MASTER_DIR.glob("*.csv"))
    print(f"Processing {len(files)} symbols...\n")

    for file in files:
        df = pd.read_csv(file)

        required = {"date", "open", "high", "low", "close"}
        if not required.issubset(df.columns):
            print(f"❌ Skipping {file.name}")
            continue

        monthly = build_monthly(df)
        out_file = OUT_DIR / file.name
        monthly.to_csv(out_file, index=False)

        print(f"✓ Monthly: {file.name}")

    print("\n✅ MONTHLY EXPIRY CANDLES CREATED")

if __name__ == "__main__":
    main()
