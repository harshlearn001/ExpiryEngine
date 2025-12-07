import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

symbol = "RELIANCE"
file_path = fr"H:\ExpiryEngine\data\master\{symbol}.csv"

df = pd.read_csv(file_path)

# Normalize (your master uses lowercase)
df.rename(columns={
    "date": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close"
}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Take only last 6 days
df = df.tail(6).reset_index(drop=True)

# spacing for 6 candles
df['x'] = df.index * 2

candle_width = 0.8
wick_width = 1

fig, ax = plt.subplots(figsize=(10, 5))

for _, row in df.iterrows():
    x = row['x']
    o = row['Open']
    h = row['High']
    l = row['Low']
    c = row['Close']

    color = "green" if c >= o else "red"

    # Wick
    ax.plot([x, x], [l, h], color=color, linewidth=wick_width)

    # Body
    rect = Rectangle(
        (x - candle_width / 2, min(o, c)),
        candle_width,
        abs(c - o),
        facecolor=color,
        edgecolor=color
    )
    ax.add_patch(rect)

# Label 6 days
ax.set_xticks(df['x'])
ax.set_xticklabels(df['Date'].dt.strftime("%d-%b"), rotation=45)

ax.grid(True, linestyle="--", alpha=0.3)
ax.set_facecolor("white")
plt.title(f"{symbol} — Daily Candles (Last 6 Days)", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Price")

plt.tight_layout()
plt.show()
