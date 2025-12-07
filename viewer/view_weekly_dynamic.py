import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

print("\n=== Weekly Candle Viewer ===")

# Ask which stock
symbol = input("Enter stock name (example: RELIANCE, TCS, HDFCBANK): ").strip().upper()

# Ask how many candles to show
try:
    last_n = int(input("How many last weekly candles to show? (default = 10): ").strip())
except:
    last_n = 10

# Build file path
file_path = fr"H:\ExpiryEngine\data\weekly\{symbol}.csv"

# Validate file
if not os.path.exists(file_path):
    print(f"\n❌ File not found: {file_path}")
    print("Make sure the symbol and file exist in: data/weekly/")
    exit()

# Load data
df = pd.read_csv(file_path)

# Standardize column names
df.rename(columns={
    "Week_Start": "Date",
    "Open": "Open",
    "High": "High",
    "Low": "Low",
    "Close": "Close"
}, inplace=True)

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Take last N candles
df = df.tail(last_n).reset_index(drop=True)

# Add spacing between candles
df["x"] = df.index * 2

candle_width = 0.8
wick_width = 1

fig, ax = plt.subplots(figsize=(12, 6))

# Draw candles
for _, row in df.iterrows():
    x = row["x"]
    o = row["Open"]
    h = row["High"]
    l = row["Low"]
    c = row["Close"]

    color = "green" if c >= o else "red"

    # Wick
    ax.plot([x, x], [l, h], color=color, linewidth=wick_width)

    # Body
    rect = Rectangle(
        (x - candle_width / 2, min(o, c)),
        candle_width,
        abs(c - o),
        facecolor=color,
        edgecolor=color,
        linewidth=1.2,
    )
    ax.add_patch(rect)

# X-axis labeling
ax.set_xticks(df["x"])
ax.set_xticklabels(df["Date"].dt.strftime("%d-%b"), rotation=45)

ax.grid(True, linestyle="--", alpha=0.3)
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

plt.title(f"{symbol} — Weekly Candles (Last {last_n} Weeks)", fontsize=15)
plt.xlabel("Week")
plt.ylabel("Price")

plt.tight_layout()
plt.show()
