import yfinance as yf #Biblioteca que permite acessar dados financeiros historicos diretamente do Yahoo Finance
import pandas as pd #Biblioteca par manipulação de dadosem formato Tabular (DataFrames), leitura e escrita de arquivos .csv
from scripts.lft_model import simulate_lft

#Função para importar dados do BOVA11, IVVB11 e IBOVESPA
def load_etfs_ibovespa(start="2015-01-01", end='2025-01-01'):
    tickers = ["BOVA11.SA", "IVVB11.SA", "^BVSP"]
    data = yf.download(tickers, start=start, end=end)["Adj Close"] #'Adj Close' -> Preço de fechameno ajustado, considera dividendos, splits e outros ajustes corporativos. Mais indicado para análises históricas de retorno.
    data.columns = ["BOVA11", 'IVVB11', 'IBOVESPA']
    return data

#Função para importar dados do XFIX11
def load_xfix11(start='2021-01-01', end='2025-01-01'):
    xfix = yf.download('XFIX11.SA', start=start, end=end)['Adj Close']
    xfix.name = 'XFIX11'
    return xfix

#Função para importar dados do IFIX
def load_ifix(csv_path='data/ifix.csv'):#csv_path é o caminho do arquivo CSV que contém os dados do IFIX
    ifix = pd.read_csv(csv_path, parse_dates=["Date"], index_col="Date")#parse_dates diz para o Pandas interpretar a coluna "Date" como datas e não como texto. Index_col define "Date" como índice do DataFrame, essencial para usar o .loc
    ifix.rename(columns={"Close": 'IFIX'}, inplace=True)
    return ifix.loc[:'2020-12-31']

#Função para junção de dados do XFIX11 e IFIX
def combine_fii_series(ifix, xfix):
    combined = pd.concat([ifix, xfix])
    combined = combined.sort_index()
    combined.name = "FII"
    return combined

lft_series = simulate_lft('data/selic_over.csv')

full.data = pd.concat([etfs, xfix_combined, lft_series], axis=1).dropna()
