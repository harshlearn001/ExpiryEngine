import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

symbol = "RELIANCE"
file_path = fr"H:\ExpiryEngine\data\weekly\{symbol}.csv"

df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Week_Start'])
df = df.sort_values('Date').reset_index(drop=True)

# Give big spacing between candles
df['x'] = df.index * 2      # spacing = 2 units per candle

candle_width = 0.9          # body width
wick_width = 1              # thin wick

fig, ax = plt.subplots(figsize=(16, 8))

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
        edgecolor=color,
        linewidth=1.2
    )
    ax.add_patch(rect)

# X-axis labeling
step = max(1, len(df) // 12)
ax.set_xticks(df['x'][::step])
ax.set_xticklabels(df['Date'].dt.strftime("%Y-%m-%d")[::step], rotation=45)

ax.grid(True, linestyle="--", alpha=0.3)
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

plt.title(f"{symbol} - Weekly Candles (With Spacing, TradingView Style)", fontsize=16)
plt.xlabel("Week")
plt.ylabel("Price")
plt.tight_layout()
plt.show()
