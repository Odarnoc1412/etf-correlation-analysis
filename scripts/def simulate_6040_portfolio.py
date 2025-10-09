def simulate_6040_portfolio(efficient_weights, etf_returns, lft_returns):
    #"Combina 60% do portfólio eficiente com 40% da LFT simulada."

    #"Parameters:"
    #"- efficient_weights: array com pesos ótimos dos ETFs"
    #"- etf_returns: DataFrame com retornos log dos ETFs"
    #"- lft_returns: Series ou DataFrame com retornos da LFT simulada"
    #"Returns:"
    #"- portfolio_returns: Series com retornos diários do portfólio 60/40"

    #Retorno do portfólio eficiente 60
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
    