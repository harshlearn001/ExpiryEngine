import os
from pathlib import Path

BASE_DIR = Path(r"H:/ExpiryEngine")

# Raw historical daily data (NSE OHLC)
RAW_DIR = BASE_DIR / "data" / "raw"

# Clean weekly/monthly candles
CLEAN_DIR = BASE_DIR / "data" / "clean"

# Ensure folders exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)
