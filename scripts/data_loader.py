import yfinance as yf #Biblioteca que permite acessar dados financeiros historicos diretamente do Yahoo Finance
import pandas as pd #Biblioteca par manipulação de dadosem formato Tabular (DataFrames), leitura e escrita de arquivos .csv
from scripts.lft_model import simulate_lft
from data_sources.selic_loader import load_selic_data
from data_sources.ifix_loader import load_ifix_data
from scripts.lft_model import simulate_lft

#Função para importar dados do BOVA11, IVVB11 e IBOVESPA
def load_etfs_ibovespa(start="2015-01-01", end='2025-01-01'):
    tickers = ["BOVA11.SA", "IVVB11.SA", "^BVSP"]
    data = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)#'Adj Close' -> Preço de fechameno ajustado, considera dividendos, splits e outros ajustes corporativos. Mais indicado para análises históricas de retorno.
    adj_close = pd.DataFrame({ticker: data[ticker]['Close'] for ticker in tickers})
    adj_close.columns = ["BOVA11", 'IVVB11', "IBOVESPA"]
    adj_close.index.name = "Date"
    return adj_close

#Função para importar dados do XFIX11
def load_xfix11(start='2021-01-12', end='2025-01-01'):
    data = yf.download('XFIX11.SA', start=start, end=end, group_by="ticker", auto_adjust=True)
    xfix = data["XFIX11.SA"]["Close"]
    xfix.name = 'XFIX11'
    return xfix

#Função para importar dados do IFIX
def load_ifix():#csv_path é o caminho do arquivo CSV que contém os dados do IFIX
    df = load_ifix_data()#parse_dates diz para o Pandas interpretar a coluna "Date" como datas e não como texto. Index_col define "Date" como índice do DataFrame, essencial para usar o .loc
    df.rename(columns={"Close": 'IFIX'}, inplace=True)
    return df['IFIX'].loc[:'2021-01-12']

#Função para junção de dados do XFIX11 e IFIX
def combine_fii_series(ifix, xfix):
    #Usando IFIX até 12/01/2021
    pre_cutoff = ifix[ifix.index <= '2021-01-12']
    #Usando XFIX a partir de 12/01/2021
    post_cutoff = xfix[xfix.index > '2021-01-12']
    combined = pd.concat([pre_cutoff, post_cutoff]).sort_index()
    combined.name = "FII"
    return combined 

selic_df = load_selic_data()
lft_series = simulate_lft(selic_df)

etfs = load_etfs_ibovespa()
xfix = load_xfix11()
ifix = load_ifix()
xfix_combined = combine_fii_series(ifix, xfix)

full_data = pd.concat([etfs, xfix_combined, lft_series], axis=1).dropna()
