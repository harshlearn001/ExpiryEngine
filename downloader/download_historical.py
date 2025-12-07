import sys
sys.path.append(r"H:/ExpiryEngine")
import os
import json
import time
import pandas as pd
import requests
from datetime import datetime
from config.settings import RAW_DIR

# -----------------------------------------
# NSE REQUEST SESSION
# -----------------------------------------
def make_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9"
    })
    session.get("https://www.nseindia.com", timeout=5)
    return session


# -----------------------------------------
# GET ALL F&O STOCK SYMBOLS
# -----------------------------------------
def get_fo_symbols(session):
    url = "https://www.nseindia.com/api/liveEquity-derivatives?index=fno_stock_lot"
    r = session.get(url, timeout=10)
    data = r.json()

    symbols = sorted({item["symbol"] for item in data.get("data", [])})

    print(f"✔ Found {len(symbols)} F&O symbols")
    return symbols


# -----------------------------------------
# DOWNLOAD HISTORICAL DATA FOR A SYMBOL
# -----------------------------------------
def download_history(session, symbol):
    url = f"https://www.nseindia.com/api/chart-databyindex?index={symbol}&preopen=true"

    try:
        r = session.get(url, timeout=10)
        data = r.json()

        points = data.get("data", [])
        if not points:
            print(f"❌ No data for {symbol}")
            return

        rows = []
        for p in points:
            rows.append({
                "date": datetime.fromtimestamp(p["CH_TIMESTAMP"]/1000).strftime("%Y-%m-%d"),
                "open": p["CH_OPENING_PRICE"],
                "high": p["CH_TRADE_HIGH_PRICE"],
                "low": p["CH_TRADE_LOW_PRICE"],
                "close": p["CH_CLOSING_PRICE"],
                "volume": p["CH_TOT_TRADED_QTY"]
            })

        df = pd.DataFrame(rows)
        df = df.dropna().sort_values("date")

        out_path = f"{RAW_DIR}/{symbol}_history.csv"
        df.to_csv(out_path, index=False)

        print(f"✔ Saved {symbol}: {len(df)} rows")

    except Exception as e:
        print(f"❌ Error downloading {symbol}: {e}")


# -----------------------------------------
# MAIN EXECUTION LOOP
# -----------------------------------------
if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)

    session = make_session()

    # Step 1: fetch F&O list
    symbols = get_fo_symbols(session)

    # Step 2: download history for each symbol
    for sym in symbols:
        download_history(session, sym)
        time.sleep(1)  # NSE protection
