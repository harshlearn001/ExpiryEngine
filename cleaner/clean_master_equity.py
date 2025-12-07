import pandas as pd
from pathlib import Path

BASE = Path(r"H:/ExpiryEngine")
MASTER = BASE / "data" / "master"
CLEAN = BASE / "data" / "clean"

CLEAN.mkdir(exist_ok=True, parents=True)

DATE_FORMATS = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]

def find_date_column(df):
    """
    Safely find a date-like column.
    """
    cols = [c.strip().lower().replace("﻿", "") for c in df.columns]  # remove BOM
    print("DEBUG → Columns:", df.columns.tolist())

    # Possible names
    candidates = ["date", "dt", "timestamp"]

    for idx, col in enumerate(cols):
        if col in candidates:
            return df.columns[idx]  # return actual name

    # If none matched, try fuzzy match
    for idx, col in enumerate(cols):
        if "date" in col:
            return df.columns[idx]

    raise Exception("❌ No date column found!")

def parse_date(df, date_col):
    # Clean column
    df[date_col] = df[date_col].astype(str).str.strip()

    # Try strict formats
    for fmt in DATE_FORMATS:
        try:
            df["date"] = pd.to_datetime(df[date_col], format=fmt, errors="raise")
            print(f"✔ Parsed using format: {fmt}")
            return df
        except:
            pass

    # Flexible fallback
    print("⚠ Using flexible parser")
    df["date"] = pd.to_datetime(df[date_col], errors="coerce")

    return df

def clean_one_file(path):
    print("\n---- Cleaning", path.name, "----")

    try:
        df = pd.read_csv(path)
    except:
        df = pd.read_csv(path, sep=None, engine="python")

    # 1️⃣ Find the date column
    date_col = find_date_column(df)

    # 2️⃣ Parse the date
    df = parse_date(df, date_col)

    # Drop invalid rows
    df = df.dropna(subset=["date"])

    # 3️⃣ Sort, do not drop old column until new date exists
    df = df.sort_values("date")

    # Optional: drop old date column
    if date_col != "date":
        df = df.drop(columns=[date_col], errors="ignore")

    # 4️⃣ Save cleaned file
    out = CLEAN / path.name
    df.to_csv(out, index=False)

    print(f"✔ CLEANED → {out} ({len(df)} rows)")

def main():
    files = list(MASTER.glob("*.csv"))
    print(f"Found {len(files)} master files")

    for f in files:
        clean_one_file(f)

if __name__ == "__main__":
    main()
