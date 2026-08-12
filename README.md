# Hyperliquid Trader Sentiment Analysis

Exploring how Bitcoin market sentiment (Fear/Greed) correlates with trader performance across ~211,000 trades on Hyperliquid, a decentralized perpetuals exchange.

## The Question

Does trader sentiment actually predict outcomes — or is it just noise? This project merges Hyperliquid's historical trade data with the Bitcoin Fear & Greed Index to look for real behavioral patterns: does performance shift with sentiment, and do traders behave differently (position sizing, frequency) depending on market mood?

## Key Findings

- **Sentiment correlates with performance** — average PnL and win rate shift measurably between Fear, Neutral, and Greed regimes.
- **Fear drives volume, not quality** — the highest trade volume occurs during Fear phases, alongside the weakest win rates.
- **Position sizing is counterintuitive** — traders don't necessarily reduce risk exactly when performance is worst.
- **Frequency beats sporadic activity** — traders who trade consistently outperform infrequent traders by a wide margin on average total PnL.

*(Exact figures depend on the dataset snapshot — run `analysis.py` to reproduce current numbers.)*

## Tech Stack

- **Python** — Pandas, NumPy for data cleaning and aggregation
- **Matplotlib / Seaborn** — visualization
- **Streamlit** — interactive dashboard UI

## Project Structure

```
├── analysis.py      # core data cleaning, merging, and stats logic
├── app.py            # Streamlit dashboard (upload-your-own-data or demo mode)
├── requirements.txt
└── data/              # local only — not tracked in this repo (see below)
```

## Running Locally

1. Clone this repo
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Add your own data files to a local `data/` folder:
   - `fear_greed_index.csv` (Bitcoin Fear & Greed Index, daily)
   - `historical_data.csv` (Hyperliquid trade history)
4. Run the analysis:
   ```
   python analysis.py
   ```
5. Launch the dashboard:
   ```
   streamlit run app.py
   ```

**Note on data:** raw trade data is not included in this repo (size and redistribution reasons). The Streamlit app supports uploading your own CSVs directly, or viewing pre-computed demo results.

## Live Demo

🔗 [Add your Streamlit Cloud link here once deployed]

## What's Next

- Deeper segmentation by trader cohort (whale vs. retail sizing)
- Time-lagged sentiment analysis (does sentiment lead or lag price movement?)
- Extending to other DEXs for cross-platform comparison
