import pandas as pd
import numpy as np
import os


def carregar_e_processar(caminho: str = "data/raw/dengue_recife.csv") -> pd.DataFrame:
    """
    Carrega os dados brutos do InfoDengue, realiza limpeza,
    engenharia de features e retorna o DataFrame pronto para modelagem.
    """

    df = pd.read_csv(caminho)

    # Converter timestamp para data legível
    df['data'] = pd.to_datetime(df['data_iniSE'], unit='ms')
    df = df.sort_values('data').reset_index(drop=True)

    # Selecionar colunas relevantes para o modelo
    colunas = [
        'data', 'SE', 'casos', 'casos_est', 'nivel',
        'tempmed', 'tempmin', 'tempmax',
        'umidmed', 'umidmin', 'umidmax',
        'p_rt1'
    ]
    df = df[colunas].copy()

    # Tratar valores ausentes com forward fill
    df.ffill(inplace=True)
    df.dropna(inplace=True)

    # Features temporais
    df['mes']    = df['data'].dt.month
    df['ano']    = df['data'].dt.year
    df['semana'] = df['data'].dt.isocalendar().week.astype(int)

    # Lag features — casos das semanas anteriores (autocorrelação temporal)
    df['casos_lag1'] = df['casos_est'].shift(1)
    df['casos_lag2'] = df['casos_est'].shift(2)
    df['casos_lag4'] = df['casos_est'].shift(4)

    # Média móvel das últimas 4 semanas
    df['media_movel_4'] = df['casos_est'].rolling(window=4).mean()

    # Remover linhas com NaN geradas pelos lags e rolling
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"Dataset processado: {df.shape}")
    print(f"Colunas: {list(df.columns)}")
    return df


def salvar_processado(
    df: pd.DataFrame,
    caminho: str = "data/processed/dengue_processado.csv"
):
    """Salva o DataFrame processado em CSV."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    df.to_csv(caminho, index=False)
    print(f"Salvo em: {caminho}")


if __name__ == "__main__":
    df = carregar_e_processar()
    salvar_processado(df)
    print(df.head())