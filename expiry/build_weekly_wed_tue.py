#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExpiryEngine
Build WEEKLY candles (Wednesday → Tuesday)
"""

import pandas as pd
from pathlib import Path

# ================= PATHS =================
MASTER_DIR = Path(r"H:\ExpiryEngine\data\master")
OUT_DIR = Path(r"H:\ExpiryEngine\data\weekly_candle_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ================= LOGIC =================
def build_weekly(df):
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Monday=0 ... Wednesday=2
    df["weekday"] = df["date"].dt.weekday

    # New week starts on Wednesday
    df["week_id"] = (df["weekday"] == 2).cumsum()

    weekly = (
        df.groupby("week_id")
        .agg(
            Week_Start=("date", "min"),
            Week_End=("date", "max"),
            Open=("open", "first"),
            High=("high", "max"),
            Low=("low", "min"),
            Close=("close", "last"),
        )
        .reset_index(drop=True)
    )

    return weekly

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

        weekly = build_weekly(df)
        out_file = OUT_DIR / file.name
        weekly.to_csv(out_file, index=False)

        print(f"✓ Weekly: {file.name}")

    print("\n✅ WEEKLY WED→TUE CANDLES CREATED")

if __name__ == "__main__":
    main()
