import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scripts.data_loader import (
    load_etfs_ibovespa,
    load_xfix11,
    load_ifix,
    load_selic_data,
    combine_fii_series
)

from scripts.lft_model import simulate_lft
from scripts.portfolio_simulator import (
    calculate_log_returns,
    simulate_by_period,
    simulate_6040_portfolio
)

from scripts.benchmarking import compare_portfolios

# Normaliza todas as séries para começar em 1.0
def normalize_series(series):
    return series / series.iloc[0]

etfs = load_etfs_ibovespa()
xfix = load_xfix11()
ifix = load_ifix()
selic_df = load_selic_data()
lft_series = simulate_lft(selic_df)
xfix_combined = combine_fii_series(ifix, xfix)

print("ifix type:", type(ifix))
print("xfix type:", type(xfix))
# Padronização dos índices para datetime.date
etfs.index = pd.to_datetime(etfs.index, dayfirst=True)
xfix_combined.index = pd.to_datetime(xfix_combined.index, dayfirst=True)
lft_series.index = pd.to_datetime(lft_series.index, dayfirst=True)

print("etfs shape:", etfs.shape)
print("xfix_combined shape:", xfix_combined.shape)
print("lft_series shape:", lft_series.shape)
print("Common index range:", etfs.index.intersection(xfix_combined.index).intersection(lft_series.index))


full_data = pd.concat([etfs, xfix_combined.to_frame(), lft_series], axis=1).loc[
    etfs.index.intersection(xfix_combined.index).intersection(lft_series.index)
]
print("full_data shape after join='inner':", full_data.shape)

print("full_data shape before dropna:", pd.concat([etfs, xfix_combined, lft_series], axis=1).shape)
print("full_data shape after dropna:", full_data.shape)
print("full_data columns:", full_data.columns)
returns_df = calculate_log_returns(full_data)
returns_df = returns_df.interpolate(method='time')
print("NaNs per columns after interpolation:")
print(returns_df.isna().sum())

periods = [10, 5, 3]
weights_dict = simulate_by_period(full_data, periods)

portfolio_returns_dict = {}

for label, weights in weights_dict.items():
    years = int(label.split('_')[0])
    cutoff = returns_df.index.max() - pd.DateOffset(years=years)
    returns_filtered = returns_df[returns_df.index > cutoff]


    ativos_usados = returns_df.columns[:len(weights)].tolist()
    clean_returns = returns_df.dropna(subset=ativos_usados + ['LFT'])

    if clean_returns.empty:
        print ('Clean Returns are empty for {label}. Passing...')
        continue


    efficient = clean_returns[ativos_usados].dot(weights)
    portfolio_returns_dict[f"Efficient_{label}"] = efficient
    portfolio_6040 = simulate_6040_portfolio(weights, clean_returns[ativos_usados], clean_returns["LFT"])
    portfolio_returns_dict[f"60_40_{label}"] = portfolio_6040

ibov_returns = returns_df["IBOVESPA"]
benchmark_df = compare_portfolios(portfolio_returns_dict, ibov_returns)

print("benchmark_df type:", type(benchmark_df))

for period in ['10_years', '5_years', '3_years']:
    plt.figure(figsize=(12,6))
    
    cutoff = returns_df.index.max() - pd.DateOffset(years=int(period.split('_')[0]))
    idx_filtered = returns_df.index[returns_df.index > cutoff]

    for key, series in portfolio_returns_dict.items():
        if key.endswith(period):
            series_filtered = series.loc[idx_filtered]
            cumulative = (1 + series_filtered).cumprod()
            plt.plot(normalize_series(cumulative), label=key)

            if 'Efficient' in key:
                weights = weights_dict[period]
                ativos = returns_df.columns[:len(weights)]
                pesos_formatados = ', '.join([f'{a}: {round(w, 2)}' for a, w in zip(ativos, weights)])
                plt.text(0.01, 0.01, f'Pesos: {pesos_formatados}', transform=plt.gca().transAxes,
                         fontsize=9, bbox=dict(facecolor='white', alpha=0.6))
    ibov_filtered = ibov_returns[series.index]
    ibov_cumulative = (1 + ibov_filtered).cumprod()
    plt.plot(normalize_series(ibov_cumulative), label='IBOVESPA', linestyle='--', color='black')

    plt.title(f'Cumulative Returns - {period}')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'dashboard/cumulative_returns_{period}.png')
    plt.close()

if benchmark_df is not None and not benchmark_df.empty:
    benchmark_df.style.format({
        "Annual Return": "{:.2%}",
        "Volatility": "{:.2%}",
        "Sharpe": "{:.2%}",
        "Tracking Error": "{:.2%}",
        "Excess Return": "{:.2%}"
    })
    benchmark_df.to_csv('dashboard/portfolio_metrics.csv', index=False)
else:
    print("Benchmark_df is empty")
plt.figure(figsize=(12,6))
for name, returns in portfolio_returns_dict.items():
    print(f"{name} → NaNs: {returns.isna().sum()}, Shape: {returns.shape}")
    cumulative = (1 + returns).cumprod()
    plt.plot(cumulative, label=name)

plt.plot((1 + ibov_returns).cumprod(), label="IBOVESPA", linestyle="--", color="black")
plt.title("Cumulative Returns Comparison")
plt.legend()
plt.grid(True)
plt.show()

benchmark_df.to_csv("dashboard/portfolio_metrics.csv", index=False)
returns_df.to_csv("dashboard/full_returns.csv")
print("Returns start:", returns_df.index.min())
print("Returns end:", returns_df.index.max()) 

print("Full data shape:", full_data.shape)
print("Returns shape:", returns_df.shape)
print("Weights dict:", weights_dict)
print("Portfolio keys:", portfolio_returns_dict.keys())
print("Benchmark head:")
print(benchmark_df.head())