"""
Trader Performance vs Market Sentiment Analysis
-------------------------------------------------
Analyzes how Bitcoin Fear/Greed sentiment relates to trader
behavior and performance on Hyperliquid (~211k trades).

Data expected in ./data/:
  - fear_greed_index.csv   (columns: timestamp, value, classification, date)
  - historical_data.csv    (Hyperliquid trade history)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")

DATA_DIR = "data"


def load_data():
    """Load sentiment and trade data from the local data/ folder."""
    sentiment_path = os.path.join(DATA_DIR, "fear_greed_index.csv")
    trades_path = os.path.join(DATA_DIR, "historical_data.csv")

    if not os.path.exists(sentiment_path) or not os.path.exists(trades_path):
        raise FileNotFoundError(
            f"Expected data files in ./{DATA_DIR}/. "
            f"Place fear_greed_index.csv and historical_data.csv there."
        )

    sentiment = pd.read_csv(sentiment_path)
    trades = pd.read_csv(trades_path)
    return sentiment, trades


def clean_and_merge(sentiment, trades):
    """Clean both datasets and merge trades with daily sentiment."""
    sentiment = sentiment.copy()
    trades = trades.copy()

    sentiment["date"] = pd.to_datetime(sentiment["date"]).dt.date

    trades["Timestamp"] = pd.to_datetime(
        trades["Timestamp IST"], errors="coerce"
    )
    trades["date"] = trades["Timestamp"].dt.date

    df = trades.merge(
        sentiment[["date", "value", "classification"]], on="date", how="left"
    )
    df = df.dropna(subset=["classification"])

    df["Closed PnL"] = pd.to_numeric(df["Closed PnL"], errors="coerce")
    df["win"] = df["Closed PnL"] > 0
    df["date"] = pd.to_datetime(df["date"])

    return df


def compute_sentiment_stats(df):
    """Aggregate PnL, win rate, avg position size, and volume by sentiment."""
    pnl = df.groupby("classification")["Closed PnL"].agg(["mean", "median", "sum"]).round(2)
    winrate = (df.groupby("classification")["win"].mean() * 100).round(1)
    volume = df.groupby("classification").size()
    avg_size = df.groupby("classification")["Size USD"].mean().round(2)

    stats = pnl.copy()
    stats["win_rate_pct"] = winrate
    stats["trade_count"] = volume
    stats["avg_position_usd"] = avg_size
    return stats


def compute_trader_segments(df):
    """Segment traders by frequency and compute performance per segment."""
    account_stats = df.groupby("Account").agg(
        total_pnl=("Closed PnL", "sum"),
        avg_pnl=("Closed PnL", "mean"),
        win_rate=("win", "mean"),
        trade_count=("Trade ID", "count"),
        avg_size=("Size USD", "mean"),
    ).reset_index()

    account_stats["frequency_segment"] = pd.qcut(
        account_stats["trade_count"], q=3, labels=["Infrequent", "Moderate", "Frequent"]
    )
    return account_stats


def plot_sentiment_charts(stats, save_path="sentiment_analysis.png"):
    order = ["Fear", "Neutral", "Greed", "Extreme Greed"]
    order = [o for o in order if o in stats.index]
    colors = {"Fear": "#e74c3c", "Neutral": "#95a5a6", "Greed": "#2ecc71", "Extreme Greed": "#f39c12"}
    palette = [colors[o] for o in order]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Trader Performance vs Market Sentiment", fontsize=16, fontweight="bold")

    axes[0, 0].bar(order, stats.loc[order, "mean"], color=palette)
    axes[0, 0].set_title("Average PnL by Sentiment")
    axes[0, 0].set_ylabel("Avg PnL (USD)")

    axes[0, 1].bar(order, stats.loc[order, "win_rate_pct"], color=palette)
    axes[0, 1].set_title("Win Rate by Sentiment")
    axes[0, 1].set_ylabel("Win Rate (%)")

    axes[1, 0].bar(order, stats.loc[order, "avg_position_usd"], color=palette)
    axes[1, 0].set_title("Avg Position Size by Sentiment")
    axes[1, 0].set_ylabel("Avg Position (USD)")

    axes[1, 1].bar(order, stats.loc[order, "trade_count"], color=palette)
    axes[1, 1].set_title("Trade Volume by Sentiment")
    axes[1, 1].set_ylabel("Number of Trades")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def get_key_insights(stats, account_stats):
    """Return the key findings as a list of strings, computed dynamically
    from whatever data is passed in (does not assume a fixed direction)."""
    insights = []

    if "Fear" in stats.index and "Greed" in stats.index:
        fear = stats.loc["Fear"]
        greed = stats.loc["Greed"]
        better, worse = (greed, fear) if greed["mean"] >= fear["mean"] else (fear, greed)
        better_name = "Greed" if better is greed else "Fear"
        worse_name = "Fear" if better is greed else "Greed"
        insights.append(
            f"{better_name} days outperform {worse_name} days: avg PnL ${better['mean']:.2f} vs "
            f"${worse['mean']:.2f}, win rate {better['win_rate_pct']:.1f}% vs {worse['win_rate_pct']:.1f}%."
        )

    if "Fear" in stats.index:
        fear = stats.loc["Fear"]
        top_volume_class = stats["trade_count"].idxmax()
        if top_volume_class == "Fear":
            insights.append(
                f"Fear drives volume: {int(fear['trade_count']):,} trades happen on Fear days "
                f"(the most of any sentiment), with a win rate of {fear['win_rate_pct']:.1f}%."
            )
        top_size_class = stats["avg_position_usd"].idxmax()
        if top_size_class == "Fear":
            insights.append(
                f"Position sizes are largest on Fear days (${fear['avg_position_usd']:.2f} avg) -- "
                f"worth checking whether this coincides with lower win rates in your data."
            )

    if not account_stats.empty and "frequency_segment" in account_stats:
        freq_pnl = account_stats.groupby("frequency_segment", observed=True)["total_pnl"].mean()
        if "Frequent" in freq_pnl.index and "Infrequent" in freq_pnl.index:
            insights.append(
                f"Frequent traders average ${freq_pnl['Frequent']:,.0f} total PnL vs "
                f"${freq_pnl['Infrequent']:,.0f} for infrequent traders."
            )

    if not insights:
        insights.append("Not enough sentiment categories in this data to generate comparative insights.")

    return insights


if __name__ == "__main__":
    sentiment, trades = load_data()
    df = clean_and_merge(sentiment, trades)
    stats = compute_sentiment_stats(df)
    account_stats = compute_trader_segments(df)

    print("=== Sentiment Stats ===")
    print(stats)

    chart_path = plot_sentiment_charts(stats)
    print(f"\nChart saved to {chart_path}")

    print("\n=== Key Insights ===")
    for i, insight in enumerate(get_key_insights(stats, account_stats), 1):
        print(f"{i}. {insight}")
