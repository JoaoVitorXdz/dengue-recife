import requests
import pandas as pd
import os

# =============================================
# COLETA DE DADOS - InfoDengue API
# Casos de dengue + dados climáticos de Recife
# =============================================

GEOCODE_RECIFE = 2611606  # Código IBGE de Recife
DISEASE = "dengue"
EW_START = 1    # semana epidemiológica início
EW_END = 52     # semana epidemiológica fim

def coletar_dados(ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    """
    Coleta dados de dengue do InfoDengue para Recife.
    Retorna um DataFrame com casos + clima por semana.
    """
    todos_dados = []

    for ano in range(ano_inicio, ano_fim + 1):
        print(f"Coletando dados de {ano}...")

        url = (
            f"https://info.dengue.mat.br/api/alertcity?"
            f"geocode={GEOCODE_RECIFE}"
            f"&disease={DISEASE}"
            f"&format=json"
            f"&ew_start={EW_START}"
            f"&ew_end={EW_END}"
            f"&ey_start={ano}"
            f"&ey_end={ano}"
        )

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            dados = response.json()
            if dados:
                df_ano = pd.DataFrame(dados)
                todos_dados.append(df_ano)
                print(f"  OK — {len(df_ano)} semanas coletadas")
        else:
            print(f"  ERRO {response.status_code} no ano {ano}")

    if todos_dados:
        df_final = pd.concat(todos_dados, ignore_index=True)
        return df_final
    else:
        print("Nenhum dado coletado.")
        return pd.DataFrame()


def salvar_dados(df: pd.DataFrame, caminho: str = "data/raw/dengue_recife.csv"):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False)
    print(f"\nDados salvos em: {caminho}")
    print(f"Total de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")


if __name__ == "__main__":
    df = coletar_dados(ano_inicio=2015, ano_fim=2024)

    if not df.empty:
        salvar_dados(df)
        print("\nPrimeiras linhas:")
        print(df.head())