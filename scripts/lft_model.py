import pandas as pd

#Função para simular o comportamento da LFT com base na Selic Over diária
#csv_path: caminho do arquivo CSV com a série histórica da Selic Over
#A série deve conter colunas "Date" e "Value" (taxa diára em %)
def simulate_lft(csv_path='data/selic_over.csv'):
    #Importa os dados
    selic = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
    selic.rename(columns={'Value': 'Selic'}, inplace=True)

    #Calcula o retorno diário da LFT com base na Selic
    selic['Daily_Return'] = selic['Selic'] / 100 / 252

    #Simula o valor acumulado da LFT ao longo do tempo
    selic['LFT'] = (1 + selic['Daily_Return']).cumprod()

    #Normaliza para a base 100 no início da série
    selic['LFT'] = selic['LFT'] / selic['LFT'].iloc[0] * 100

    return selic [['LFT']]
