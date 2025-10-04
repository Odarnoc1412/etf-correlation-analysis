import pandas as pd
import numpy as np
from scipy.optimize import minimize

#Função para calcular retornos logarítmicos
def calculate_log_returns(price_df):
    return np.log(price_df / price_df.shift(1)).dropna()

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

    result = minimze(portfolio_metrics, initial_weights, args=(returns,), method='SLSQP', bounds=bounds, constraints=constraints)

    return result.x #pesos ótimos

#Função para simular portfólios por período
def simulate_by_period(price_df, periods):
    portfolios = {}
    for years in periods:
        cutoff = price_df.index[-1] - pd.DateOffset(years=years)
        filtered = price_df[price_df.index >= cutoff]
        returns = calculate_log_returns(filtered)
        weights = simulate_efficient_portfolio(returns)
        portfolios[f'{years}_years'] = weights
    return portfolios