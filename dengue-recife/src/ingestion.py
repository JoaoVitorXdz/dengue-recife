import requests
import pandas as pd
import os


# =============================================
# COLETA DE DADOS — InfoDengue API
# Casos de dengue + dados climáticos de Recife
# =============================================

GEOCODE_RECIFE = 2611606  # Código IBGE de Recife
DISEASE        = "dengue"
EW_START       = 1        # Semana epidemiológica início
EW_END         = 52       # Semana epidemiológica fim


def coletar_dados(ano_inicio: int, ano_fim: int) -> pd.DataFrame:
    """
    Coleta dados de dengue do InfoDengue para Recife.

    Parâmetros:
        ano_inicio: primeiro ano a coletar (ex: 2015)
        ano_fim:    último ano a coletar  (ex: 2024)

    Retorna:
        DataFrame com casos + clima por semana epidemiológica.
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

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                dados = response.json()
                if dados:
                    df_ano = pd.DataFrame(dados)
                    todos_dados.append(df_ano)
                    print(f"  OK — {len(df_ano)} semanas coletadas")
                else:
                    print(f"  Aviso: nenhum dado retornado para {ano}")
            else:
                print(f"  ERRO HTTP {response.status_code} no ano {ano}")

        except requests.exceptions.Timeout:
            print(f"  ERRO: timeout ao coletar {ano} — pulando")
        except requests.exceptions.RequestException as e:
            print(f"  ERRO de conexão em {ano}: {e}")

    if todos_dados:
        df_final = pd.concat(todos_dados, ignore_index=True)
        return df_final

    print("Nenhum dado coletado.")
    return pd.DataFrame()


def salvar_dados(
    df: pd.DataFrame,
    caminho: str = "data/raw/dengue_recife.csv"
):
    """Salva os dados brutos em CSV."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False)
    print(f"\nDados salvos em: {caminho}")
    print(f"Total de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")


if __name__ == "__main__":
    df = coletar_dados(ano_inicio=2013, ano_fim=2024)

    if not df.empty:
        salvar_dados(df)
        print("\nPrimeiras linhas:")
        print(df.head())