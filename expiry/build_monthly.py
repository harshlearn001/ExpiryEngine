"""
ExpiryEngine - Monthly Candle Builder
Creates Tuesday → Tuesday Monthly OHLC candles
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from utils_expiry import ensure_directory


def normalize_columns(df):
    """Normalize lowercase NSE format to expected names."""
    col_map = {
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
    }
    return df.rename(columns=col_map)


def group_month_tuesday(df):
    """
    Assign each row to its monthly Tuesday group.
    A month is defined from 1st Tuesday → next month 1st Tuesday.
    """

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['weekday'] = df['Date'].dt.weekday  # Monday=0, Tuesday=1

    # Identify each month's FIRST TUESDAY
    df['is_first_tuesday'] = (
        (df['Date'].dt.weekday == 1) &        # Tuesday
        (df['Date'].dt.day <= 7)              # First 7 days of month
    )

    # Create month cycle groups
    df['month_group'] = df['is_first_tuesday'].cumsum()

    return df


def build_monthly_candles(df):
    """Aggregate into monthly OHLC candles."""
    monthly = df.groupby('month_group').agg(
        Month_Start=("Date", "min"),
        Month_End=("Date", "max"),
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last")
    ).reset_index(drop=True)

    return monthly


def process_symbol(input_path, output_path):
    df = pd.read_csv(input_path)

    df = normalize_columns(df)
    df = group_month_tuesday(df)

    required = {"Date", "Open", "High", "Low", "Close"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns in {input_path}")

    monthly = build_monthly_candles(df)

    ensure_directory(os.path.dirname(output_path))
    monthly.to_csv(output_path, index=False)

    print(f"✓ Monthly saved: {output_path}")


def main():
    master_dir = "data/master"
    output_dir = "data/monthly"

    ensure_directory(output_dir)

    symbols = [f for f in os.listdir(master_dir) if f.endswith(".csv")]

    print(f"Processing {len(symbols)} symbols...\n")

    for file in symbols:
        input_path = os.path.join(master_dir, file)
        output_path = os.path.join(output_dir, file)
        process_symbol(input_path, output_path)

    print("\n=== MONTHLY BUILD COMPLETE ===")


if __name__ == "__main__":
    main()
