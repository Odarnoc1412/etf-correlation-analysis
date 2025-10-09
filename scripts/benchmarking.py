import pandas as pd 
import numpy as np

#Retorno anualizado
def annualized_return(returns):
    return returns.mean() * 252

#Volatilidade anualizada
def annualized_volatility(returns):
    return returns.std() * np.sqrt(252)

#Sharpe ratio (sem ajuste de risco livre por enquanto)
def sharpe_ratio(returns):
    return annualized_return(returns) / annualized_volatility(returns)

#Função para comparar portfólios
def compare_portfolios(portfolio_returns_dict, benchmark_returns):
    """
    Compara múltiplos portfólios com o benchmark.
    
    Parameters:
    - portfolio_returns_dict: dict com nome e Series de retornos
    - benchmark_returns: Series com retornos do IBOVESPA
    
    Returns:
    - DataFrame com métricas comparativas
    """
    comparison = []

    for name, returns in portfolio_returns_dict.items():
        aligned_index = returns.index.intersection(benchmark_returns.index)
        port = returns.loc[aligned_index]
        bench = benchmark_returns.loc[aligned_index]

        metrics = {
            'Portfolio': name,
            'Annual Return': annualized_return(port),
            'Volatility': annualized_volatility(port),
            'Sharpe': sharpe_ratio(port),
            'Tracking Error': np.std(port - bench) * np.sqrt(252),
            'Excess Return': annualized_return(port) - annualized_return(bench)
        }
        comparison.append(metrics)
    return pd.DataFrame(comparison)