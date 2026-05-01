import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
import os

def carregar_dados(caminho: str = "data/processed/dengue_processado.csv"):
    df = pd.read_csv(caminho)
    df['data'] = pd.to_datetime(df['data'])
    return df

def preparar_features(df: pd.DataFrame):
    features = ['mes', 'semana', 'tempmed', 'tempmin', 'tempmax',
                'umidmed', 'umidmin', 'umidmax', 'p_rt1',
                'casos_lag1', 'casos_lag2', 'casos_lag4', 'media_movel_4']
    target = 'casos_est'
    X = df[features]
    y = df[target]
    return X, y, features

def avaliar_modelo(nome, modelo, X_train, X_test, y_train, y_test):
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2   = r2_score(y_test, y_pred)
    print(f"\n{nome}")
    print(f"  MAE:  {mae:.1f} casos")
    print(f"  RMSE: {rmse:.1f} casos")
    print(f"  R²:   {r2:.3f}")
    return modelo, y_pred, {'nome': nome, 'MAE': mae, 'RMSE': rmse, 'R2': r2}

def plotar_comparacao(df_test, resultados_pred, nome_modelo, y_pred):
    os.makedirs("outputs", exist_ok=True)
    plt.figure(figsize=(14, 4))
    plt.plot(df_test['data'].values, df_test['casos_est'].values,
             label='Real', color='crimson', linewidth=1.5)
    plt.plot(df_test['data'].values, y_pred,
             label=f'Previsto ({nome_modelo})', color='steelblue',
             linewidth=1.5, linestyle='--')
    plt.title(f'Previsão de casos de dengue — {nome_modelo}')
    plt.xlabel('Data')
    plt.ylabel('Casos estimados')
    plt.legend()
    plt.tight_layout()
    fname = f"outputs/previsao_{nome_modelo.lower().replace(' ','_')}.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Gráfico salvo: {fname}")

def plotar_importancia(modelo, features):
    importancias = pd.Series(modelo.feature_importances_, index=features)
    importancias.sort_values().plot(kind='barh', figsize=(8, 5), color='steelblue')
    plt.title('Importância das features — XGBoost')
    plt.tight_layout()
    plt.savefig('outputs/importancia_features.png', dpi=150)
    plt.show()

if __name__ == "__main__":
    df = carregar_dados()
    X, y, features = preparar_features(df)

    # Split temporal (80% treino, 20% teste)
    split = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    df_test = df.iloc[split:].reset_index(drop=True)

    print(f"Treino: {len(X_train)} semanas | Teste: {len(X_test)} semanas")

    resultados = []

    # 1. Regressão Linear (baseline)
    lr, pred_lr, res_lr = avaliar_modelo(
        "Regressão Linear",
        LinearRegression(),
        X_train, X_test, y_train, y_test
    )
    resultados.append(res_lr)
    plotar_comparacao(df_test, None, "Regressão Linear", pred_lr)

    # 2. Random Forest
    rf, pred_rf, res_rf = avaliar_modelo(
        "Random Forest",
        RandomForestRegressor(n_estimators=200, random_state=42),
        X_train, X_test, y_train, y_test
    )
    resultados.append(res_rf)
    plotar_comparacao(df_test, None, "Random Forest", pred_rf)

    # 3. XGBoost
    xgb, pred_xgb, res_xgb = avaliar_modelo(
        "XGBoost",
        XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42),
        X_train, X_test, y_train, y_test
    )
    resultados.append(res_xgb)
    plotar_comparacao(df_test, None, "XGBoost", pred_xgb)
    plotar_importancia(xgb, features)

    # Tabela comparativa
    print("\n=== COMPARATIVO FINAL ===")
    print(pd.DataFrame(resultados).to_string(index=False))