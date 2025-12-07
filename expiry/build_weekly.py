"""
ExpiryEngine - Weekly Candle Builder
Creates Tuesday → Tuesday weekly OHLC candles
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from utils_expiry import ensure_directory


def normalize_columns(df):
    """
    Normalize column names so different datasets can be handled.
    Converts lowercase NSE format to Title Case required for weekly candles.
    """
    col_map = {
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
    }

    df = df.rename(columns=col_map)
    return df


def build_weekly_candles(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    df["weekday"] = df["Date"].dt.weekday  # Monday=0, Tuesday=1
    df["week_group"] = (df["weekday"] == 1).cumsum()  # Start new week on Tuesday

    weekly = df.groupby("week_group").agg(
        Week_Start=("Date", "min"),
        Week_End=("Date", "max"),
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last")
    ).reset_index(drop=True)

    return weekly


def process_symbol(input_path, output_path):
    df = pd.read_csv(input_path)

    # Normalize to standard column names
    df = normalize_columns(df)

    required = {"Date", "Open", "High", "Low", "Close"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns in {input_path}: {required - set(df.columns)}")

    weekly = build_weekly_candles(df)

    ensure_directory(os.path.dirname(output_path))
    weekly.to_csv(output_path, index=False)

    print(f"✓ Weekly saved: {output_path}")


def main():
    master_dir = "data/master"
    output_dir = "data/weekly"

    ensure_directory(output_dir)

    symbols = [f for f in os.listdir(master_dir) if f.endswith(".csv")]

    print(f"Processing {len(symbols)} symbols...\n")

    for file in symbols:
        input_path = os.path.join(master_dir, file)
        output_path = os.path.join(output_dir, file)
        process_symbol(input_path, output_path)

    print("\n=== WEEKLY BUILD COMPLETE ===")


if __name__ == "__main__":
    main()
