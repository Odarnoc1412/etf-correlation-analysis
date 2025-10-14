# ETF Correlation & Portfolio Efficiency Analysis 🇧🇷📊

This project explores portfolio construction and performance analysis using Brazilian ETFs — combining Python, R, and Business Intelligence tools, with support from Microsoft Copilot.

---

## 🎯 Project Overview

The goal is to simplify investment strategies using accessible, representative assets from the Brazilian market:

- **BOVA11** → Brazilian equities
- **IVVB11** → U.S. equities (USD exposure)
- **FII** → Real estate funds (combined from IFIX and XFIX11)

We simulate efficient portfolios across three timeframes: **10, 5, and 3 years**, comparing them to:

- **IBOVESPA** (benchmark)
- A **60/40 portfolio** → 60% efficient portfolio + 40% LFT (risk-free asset)

---

## 🧠 Technical Highlights

- Data collection and normalization from multiple sources (ETFs, IFIX, Selic)
- LFT simulation based on daily Selic rates
- Efficient frontier modeling using Sharpe Ratio optimization
- Equal-weight portfolio simulation for comparison
- Modular code structure for reuse and scalability
- Visual outputs: cumulative returns, portfolio metrics, and weight distributions

---

## 🔌 API Setup: brapi.dev

To access IFIX data via the Brapi API:

1. Create a free account at [brapi.dev](https://brapi.dev)
2. Generate your API key
3. Create a file named `config_loader.py` with:

```python
BRAPI_TOKEN = "your_api_key_here"
4. Run ifix_loader.py to download IFIX data

5. Ensure ifix_snapshot.csv is saved in the data_sources/ directory
The pipeline uses load_ifix_data() to load and filter IFIX data up to January 12, 2021.

Repository Structure
├── scripts/
│   ├── data_loader.py
│   ├── lft_model.py
│   ├── portfolio_simulator.py
│   ├── benchmarking.py
│   └── test_pipeline.py
├── dashboard/
│   ├── cumulative_returns_*.png
│   └── portfolio_metrics.csv
├── data_sources/
│   └── ifix_snapshot.csv
├── README.md

Next Steps
Rebuild the project in R using equal-weight portfolios

Visualize results in Power BI

Explore advanced metrics: max drawdown, beta, alpha, and monthly rebalancing

LinkedIn Post
Check out the project summary and visuals on  [LinkedIn Profile](https://www.linkedin.com/in/conrado-ara%C3%BAjo-travassos-5bbb87167/)
Contributions & Feedback
Open to suggestions, collaborations, and feedback — feel free to reach out or fork the repo!
