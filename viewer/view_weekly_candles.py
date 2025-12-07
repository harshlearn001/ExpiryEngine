import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

BASE = Path(r"H:\ExpiryEngine\data\weekly")

def load_df(symbol):
    file = BASE / f"{symbol}.csv"
    df = pd.read_csv(file)

    # weekly file uses "start" column, not "week"
    if "start" in df.columns:
        df["start"] = pd.to_datetime(df["start"])
    else:
        raise KeyError("Column 'start' not found in weekly file!")

    return df

def plot_candles(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["start"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
        increasing_fillcolor="#26a69a",
        decreasing_fillcolor="#ef5350",
        line_width=1
    ))

    fig.update_layout(
        title=f"Weekly Candlestick Chart — {symbol}",
        xaxis_title="Week Start",
        yaxis_title="Price",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=700
    )

    fig.show()

def main():
    symbols = sorted([p.stem for p in BASE.glob("*.csv")])
    print("\nAvailable symbols:\n" + ", ".join(symbols) + "\n")

    symbol = input("Enter symbol: ").strip().upper()
    df = load_df(symbol)
    plot_candles(df, symbol)

if __name__ == "__main__":
    main()
