import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ==============================
#  SIMPLE TRADINGVIEW CANDLE VIEWER
# ==============================

# 👉 Change this to your file path
file_path = "data/weekly/RELIANCE.csv"    # example for weekly Reliance

# Load data
df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Week_Start'])  # weekly file uses Week_Start
df = df.sort_values('Date').reset_index(drop=True)

# Create numeric X axis (TradingView spacing)
df['x'] = df.index

# Create figure
fig, ax = plt.subplots(figsize=(16,7))

candle_width = 0.6    # bold body
wick_width = 0.8       # thin wick

for _, row in df.iterrows():
    x = row['x']
    o = row['Open']
    h = row['High']
    l = row['Low']
    c = row['Close']

    # Bullish = green, Bearish = red
    color = 'green' if c >= o else 'red'

    # Wick
    ax.plot([x, x], [l, h], color=color, linewidth=wick_width)

    # Body
    rect = Rectangle(
        (x - candle_width/2, min(o, c)),
        candle_width,
        abs(c - o),
        facecolor=color,
        edgecolor=color,
        linewidth=1.2
    )
    ax.add_patch(rect)

# Grid and labels
step = max(1, len(df)//12)
ax.set_xticks(df['x'][::step])
ax.set_xticklabels(df['Date'].dt.strftime("%Y-%m-%d")[::step], rotation=45)

plt.title("Candlestick Chart (TradingView Style)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()
plt.show()
