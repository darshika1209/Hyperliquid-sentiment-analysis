"""
Streamlit UI — Trader Sentiment Analysis Dashboard
----------------------------------------------------
Run locally:   streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import clean_and_merge, compute_sentiment_stats, compute_trader_segments, get_key_insights

st.set_page_config(page_title="Trader Sentiment Analysis", layout="wide")

st.title("📊 Trader Performance vs Market Sentiment")
st.caption("Analyzing ~211,000 Hyperliquid trades against the Bitcoin Fear & Greed Index")

st.sidebar.header("Data Input")
mode = st.sidebar.radio("Choose data source:", ["Upload my own CSVs", "View demo results"])

if mode == "Upload my own CSVs":
    sentiment_file = st.sidebar.file_uploader("Fear & Greed Index CSV", type="csv")
    trades_file = st.sidebar.file_uploader("Hyperliquid Trade History CSV", type="csv")

    if sentiment_file and trades_file:
        sentiment = pd.read_csv(sentiment_file)
        trades = pd.read_csv(trades_file)

        with st.spinner("Cleaning and merging data..."):
            df = clean_and_merge(sentiment, trades)
            stats = compute_sentiment_stats(df)
            account_stats = compute_trader_segments(df)

        st.success(f"Loaded {len(df):,} merged trade records")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Stats by Sentiment")
            st.dataframe(stats)
        with col2:
            st.subheader("Key Insights")
            for insight in get_key_insights(stats, account_stats):
                st.markdown(f"- {insight}")

        st.subheader("Visualizations")
        order = [o for o in ["Fear", "Neutral", "Greed", "Extreme Greed"] if o in stats.index]
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes[0, 0].bar(order, stats.loc[order, "mean"])
        axes[0, 0].set_title("Avg PnL by Sentiment")
        axes[0, 1].bar(order, stats.loc[order, "win_rate_pct"])
        axes[0, 1].set_title("Win Rate by Sentiment")
        axes[1, 0].bar(order, stats.loc[order, "avg_position_usd"])
        axes[1, 0].set_title("Avg Position Size by Sentiment")
        axes[1, 1].bar(order, stats.loc[order, "trade_count"])
        axes[1, 1].set_title("Trade Volume by Sentiment")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Upload both CSV files in the sidebar to run the analysis.")

else:
    st.info(
        "Demo mode shows the pre-computed results from the original 211k-trade dataset "
        "(not re-uploaded here for size/licensing reasons)."
    )
    st.subheader("Key Insights")
    demo_insights = [
        "Greed days outperform Fear days: avg PnL $87.89 vs $50.05, win rate 44.6% vs 41.5%.",
        "Fear drives volume, not quality: 133,871 trades happen on Fear days (the most of any "
        "sentiment) but with the lowest win rate.",
        "Position sizes are larger on Fear days ($5,259 avg) despite worse outcomes -- traders "
        "take more risk exactly when they're performing worst.",
        "Frequent traders earn far more: $480k avg total PnL vs $156k for infrequent traders.",
    ]
    for insight in demo_insights:
        st.markdown(f"- {insight}")

    st.subheader("Chart")
    st.image("sentiment_analysis.png", caption="Trader Performance vs Market Sentiment")

st.sidebar.markdown("---")
st.sidebar.markdown("[View source on GitHub](https://github.com/darshika1209/primetrade-sentiment-analysis)")
