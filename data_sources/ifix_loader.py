
import pandas as pd


def fetch_and_save_ifix_snapshot():
    import requests
    from config_loader import BRAPI_API_KEY
    url = f"https://brapi.dev/api/quote/IFIX.SA?range=10y&interval=1d&token={BRAPI_API_KEY}"
    response = requests.get(url)
    data = response.json()

    # ✅ Verificação defensiva
    if 'results' not in data or 'historicalDataPrice' not in data['results'][0]:
        raise ValueError(f"Resposta inesperada da API: {data}")

    price = data['results'][0]['historicalDataPrice']
    df = pd.DataFrame(price)
    df['date'] = pd.to_datetime(df["date"])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df['close'] = df['close'].astype(float)
    df.to_csv("data_sources/ifix_snapshot.csv")
    print("IFIX snapshot salvo com sucesso.")

def load_ifix_data():
    df = pd.read_csv("data_sources/ifix_snapshot.csv", encoding="utf-8", delimiter=",")
    
    # Converte a coluna de data
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df.set_index("Data", inplace=True)
    df.sort_index(inplace=True)

    # Renomeia a coluna de fechamento ("Último") para "IFIX"
    df.rename(columns={"Último": "IFIX"}, inplace=True)

    # Remove valores não numéricos (como vírgulas ou pontos)
    df["IFIX"] = df["IFIX"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

    # Filtra até 31/12/2020
    return df.loc[:'2021-01-12'][["IFIX"]]

if __name__ == "__main__": #garante que o script seja rodado quando executado diretamente e não quando for importado por outro módulo
    fetch_and_save_ifix_snapshot()
