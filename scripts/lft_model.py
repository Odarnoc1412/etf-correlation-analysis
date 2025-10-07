import pandas as pd

"""
    Simula o comportamento da LFT com base na Selic Over diária.
    
    Parâmetros:
    - selic_df: DataFrame com índice de datas e coluna 'Selic' em percentual anual
    
    Retorna:
    - DataFrame com coluna 'LFT' representando a curva acumulada normalizada
    """
def simulate_lft(selic_df):
    selic = selic_df.copy()

    #Calcula o retorno diário da LFT com base na Selic
    selic['Daily_Return'] = selic['SELIC'] / 100 / 252

    #Simula o valor acumulado da LFT ao longo do tempo
    selic['LFT'] = (1 + selic['Daily_Return']).cumprod()

    #Normaliza para a base 100 no início da série
    selic['LFT'] = selic['LFT'] / selic['LFT'].iloc[0] * 100

    return selic [['LFT']]
