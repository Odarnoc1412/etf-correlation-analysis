import pandas as pd
import numpy as np
from scipy.optimize import minimize

#Função para calcular retornos logarítmicos
def calculate_log_returns(price_df):
    return np.log(price_df / price_df.shift(1)).dropna(how="all")
    print("Returns_df after log calc:", returns.shape)

#Função para métricas de portfólio
def portfolio_metrics(weights, returns):
    portfolio_return = np.dot(weights, returns.mean()) * 252
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility
    return -sharpe_ratio #Negativo para maximização via minimização

#Função para simular portfólio eficiente
def simulate_efficient_portfolio(returns):
    num_assets = returns.shape[1]
    initial_weights = np.ones(num_assets) / num_assets
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

    result = minimize(portfolio_metrics, initial_weights, args=(returns,), method='SLSQP', bounds=bounds, constraints=constraints)

    return result.x #pesos ótimos

#Função para simular portfólios por período
def simulate_by_period(price_df, periods):
    portfolios = {}
    for years in periods:
        cutoff = price_df.index[-1] - pd.DateOffset(years=years)
        filtered = price_df[price_df.index >= cutoff]
        print(f"Simulating for {years} years → cutoff: {cutoff}, filtered shape: {filtered.shape}")
        if filtered.empty or filtered.shape[0] < 30:  # menos de 30 dias úteis, por exemplo
            print(f"Not enough data for {years} year. Passing...")
            continue
        
        returns = calculate_log_returns(filtered)

        if returns.empty or returns.isna().all().any():
            print(f"Invalid Returns {years} years. Passing...")
            continue

        weights = simulate_efficient_portfolio(returns)
        portfolios[f'{years}_years'] = weights
    return portfolios

def simulate_6040_portfolio(efficient_weights, etf_returns, lft_returns):
    #"Combina 60% do portfólio eficiente com 40% da LFT simulada."

    #"Parameters:"
    #"- efficient_weights: array com pesos ótimos dos ETFs"
    #"- etf_returns: DataFrame com retornos log dos ETFs"
    #"- lft_returns: Series ou DataFrame com retornos da LFT simulada"
    #"Returns:"
    #"- portfolio_returns: Series com retornos diários do portfólio 60/40"

    #Retorno do portfólio eficiente 60%
    efficient_portfolio = etf_returns.dot(efficient_weights)

    #Garantir que lft_returns seja Series
    if isinstance(lft_returns, pd.DataFrame):
        lft_returns = lft_returns.squeeze()

    #Alinhar Datas
    common_index = efficient_portfolio.index.intersection(lft_returns.index)
    efficient_portfolio = efficient_portfolio.loc[common_index]
    lft_returns = lft_returns.loc[common_index]

    #Combinar 60/40
    combined_returns = 0.6 * efficient_portfolio + 0.4 * lft_returns

    return combined_returns

