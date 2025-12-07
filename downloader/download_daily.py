import os
import pandas as pd
from datetime import datetime
from config.settings import DAILY_RAW_DIR

def download_symbol(symbol):
    """Placeholder: create dummy CSV file."""
    df = pd.DataFrame({
        "date": [datetime.today().strftime("%Y-%m-%d")],
        "open": [100],
        "high": [105],
        "low": [99],
        "close": [102],
        "volume": [123456],
    })
    out_file = f"{DAILY_RAW_DIR}/{symbol}_{df['date'][0]}.csv"
    df.to_csv(out_file, index=False)
    print(f"✔ downloaded: {out_file}")

if __name__ == "__main__":
    symbols = ["RELIANCE", "TCS", "INFY"]  # example
    for sym in symbols:
        download_symbol(sym)
