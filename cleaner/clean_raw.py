import pandas as pd
import glob
from config.settings import DAILY_RAW_DIR, RAW_DIR
import os

if __name__ == "__main__":
    files = glob.glob(f"{DAILY_RAW_DIR}/*.csv")
    for f in files:
        df = pd.read_csv(f)
        df = df.dropna()
        df.to_csv(f.replace("daily_raw", "raw"), index=False)
        print("✔ cleaned:", f)
