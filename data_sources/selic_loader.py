import pandas as pd
from datetime import datetime

def load_selic_from_csv():
    try:
        df = pd.read_csv("data_sources/selic_snapshot.csv", parse_dates=['data'], index_col='data')
        return df
    except Exception as e:
        print('Error in loading local SELIC:', e)
        return pd.DataFrame()

def fetch_selic_from_api():
    end_date = datetime.today().strftime("%d/%m/%Y")
    start_date = (datetime.today().replace(year=datetime.today().year - 10)).strftime("%d/%m/%Y")

    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial={start_date}&dataFinal={end_date}"

    try:
        df_raw = pd.read_csv(url, sep=';', parse_dates=['data'])
        if 'data' not in df_raw.columns or 'valor' not in df_raw.columns:
            raise ValueError("There is no columns on SELIC CSV")
        df_raw['data'] = pd.to_datetime(df_raw['data'], dayfirst=True)
        df_raw.set_index('data', inplace=True)
        df_raw.rename(columns={'valor': 'SELIC'}, inplace=True)
        df_raw["SELIC"] = df_raw['SELIC'].str.replace(',', '.').astype(float)
        df_raw.to_csv("data_sources/selic_snapshot.csv")
        return df_raw

    except Exception as e:
        print("Error in loading SELIC from API:", e)
        return pd.DataFrame()
    
def load_selic_data():
    return load_selic_from_csv()

if __name__ == '__main__':
    df = fetch_selic_from_api()
    print(df.head())
