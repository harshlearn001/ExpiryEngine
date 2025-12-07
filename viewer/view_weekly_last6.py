import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ==========================
# WEEKLY LAST 6 CANDLES (TradingView style)
# ==========================

symbol = "RELIANCE"
file_path = fr"H:\ExpiryEngine\data\weekly\{symbol}.csv"

# Load weekly data
df = pd.read_csv(file_path)

# Rename for safety
df.rename(columns={
    "Week_Start": "Date",
    "Open": "Open",
    "High": "High",
    "Low": "Low",
    "Close": "Close"
}, inplace=True)

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Only last 6 weekly candles
df = df.tail(6).reset_index(drop=True)

# Add spacing between candles (just like daily script)
df["x"] = df.index * 2

candle_width = 0.8
wick_width = 1

fig, ax = plt.subplots(figsize=(10, 5))

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

# X-axis labels for 6 weeks
ax.set_xticks(df["x"])
ax.set_xticklabels(df["Date"].dt.strftime("%d-%b"), rotation=45)

# Clean TradingView style
ax.grid(True, linestyle="--", alpha=0.3)
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

plt.title(f"{symbol} — Weekly Candles (Last 6 Weeks)", fontsize=14)
plt.xlabel("Week")
plt.ylabel("Price")

plt.tight_layout()
plt.show()
