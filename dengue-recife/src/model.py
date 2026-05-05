"""
src/model.py
Treinamento, avaliação e validação cruzada dos modelos de ML.
Os gráficos são delegados para src/visualization.py.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, KFold
from xgboost import XGBRegressor

from src.visualization import (
    plotar_comparacao,
    plotar_importancia,
    plotar_comparativo_modelos,
)


def carregar_dados(caminho: str = "data/processed/dengue_processado.csv") -> pd.DataFrame:
    """Carrega o dataset processado e converte a coluna de data."""
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(df["data"])
    return df


def preparar_features(df: pd.DataFrame):
    """
    Separa features (X) e target (y).

    Features usadas:
        - Temporais: mes, semana
        - Climáticas: tempmed, tempmin, tempmax, umidmed, umidmin, umidmax, p_rt1
        - Lag features: casos_lag1, casos_lag2, casos_lag4
        - Média móvel: media_movel_4

    Target: casos_est (casos estimados da semana)
    """
    features = [
        "mes", "semana",
        "tempmed", "tempmin", "tempmax",
        "umidmed", "umidmin", "umidmax",
        "p_rt1",
        "casos_lag1", "casos_lag2", "casos_lag4",
        "media_movel_4",
    ]
    target = "casos_est"
    return df[features], df[target], features


def validacao_cruzada(nome: str, modelo, X, y, n_splits: int = 5) -> dict:
    """
    Validação cruzada com K-Fold temporal.

    Usa shuffle=False para preservar a ordem temporal das semanas,
    evitando vazamento de dados futuros para o treino (data leakage).

    Parâmetros:
        nome:     nome do modelo (para exibição)
        modelo:   instância do estimador sklearn/xgboost
        X:        features completas
        y:        target completo
        n_splits: número de folds (padrão 5)

    Retorna:
        dict com média e desvio padrão do R² nos K folds
    """
    kf = KFold(n_splits=n_splits, shuffle=False)

    scores_r2  = cross_val_score(modelo, X, y, cv=kf, scoring="r2")
    scores_mae = cross_val_score(modelo, X, y, cv=kf,
                                 scoring="neg_mean_absolute_error")

    r2_media  = scores_r2.mean()
    r2_std    = scores_r2.std()
    mae_media = (-scores_mae).mean()

    print(f"  Cross-validation ({n_splits}-fold):")
    print(f"    R²  médio: {r2_media:.3f} ± {r2_std:.3f}")
    print(f"    MAE médio: {mae_media:.1f} casos")

    return {
        "cv_r2_mean": round(r2_media, 3),
        "cv_r2_std":  round(r2_std, 3),
        "cv_mae":     round(mae_media, 1),
    }


def avaliar_modelo(nome: str, modelo, X_train, X_test, y_train, y_test) -> tuple:
    """
    Treina o modelo, avalia no conjunto de teste e exibe métricas.

    Retorna:
        (modelo_treinado, y_pred, dict_de_metricas)
    """
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2   = r2_score(y_test, y_pred)

    print(f"\n{nome}")
    print(f"  MAE:  {mae:.1f} casos")
    print(f"  RMSE: {rmse:.1f} casos")
    print(f"  R²:   {r2:.3f}")

    return modelo, y_pred, {"nome": nome, "MAE": mae, "RMSE": rmse, "R2": r2}


if __name__ == "__main__":
    df = carregar_dados()
    X, y, features = preparar_features(df)

    # ── Split temporal: 80% treino / 20% teste ──────────────
    split   = int(len(df) * 0.8)
    X_train = X.iloc[:split];  X_test = X.iloc[split:]
    y_train = y.iloc[:split];  y_test = y.iloc[split:]
    df_test = df.iloc[split:].reset_index(drop=True)

    print(f"Treino: {len(X_train)} semanas | Teste: {len(X_test)} semanas\n")

    modelos = [
        ("Regressão Linear", LinearRegression()),
        ("Random Forest",    RandomForestRegressor(n_estimators=200, random_state=42)),
        ("XGBoost",          XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42)),
    ]

    resultados = []

    for nome, estimador in modelos:
        # Avaliação no conjunto de teste
        modelo_fit, y_pred, res = avaliar_modelo(
            nome, estimador, X_train, X_test, y_train, y_test
        )

        # Validação cruzada (K-Fold temporal, 5 folds)
        cv = validacao_cruzada(nome, estimador, X, y)
        res.update(cv)
        resultados.append(res)

        # Gráfico real vs previsto (delegado ao visualization.py)
        plotar_comparacao(df_test, nome, y_pred)

    # Importância das features do XGBoost
    xgb_fit = modelos[2][1]  # já treinado na iteração anterior
    plotar_importancia(xgb_fit, features)

    # Gráfico comparativo dos 3 modelos
    plotar_comparativo_modelos(resultados)

    # Tabela final
    print("\n=== COMPARATIVO FINAL ===")
    cols = ["nome", "MAE", "RMSE", "R2", "cv_r2_mean", "cv_r2_std", "cv_mae"]
    print(pd.DataFrame(resultados)[cols].to_string(index=False))