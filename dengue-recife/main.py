from src.processing import carregar_e_processar, salvar_processado
from src.visualization import gerar_grafico_casos
from src.mapa_bairros import gerar_mapa_bairros
from src.report import gerar_ppt
from src.model import (
    carregar_dados,
    preparar_features,
    avaliar_modelo,
    plotar_comparacao,
    plotar_importancia
)
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import joblib
import os
import pandas as pd


def main():
    print("🚀 Iniciando pipeline...\n")

    # ── 1. Carregar e processar dados ──────────────────────
    print("📦 Etapa 1: Processando dados...")
    df = carregar_e_processar("data/raw/dengue_recife.csv")
    salvar_processado(df)

    # ── 2. Gerar gráficos de análise exploratória ──────────
    print("\n📊 Etapa 2: Gerando gráficos...")
    gerar_grafico_casos(df)

    # ── 3. Treinar e avaliar modelos ML ────────────────────
    print("\n🤖 Etapa 3: Treinando modelos...")
    df_model = carregar_dados()
    X, y, features = preparar_features(df_model)

    # Split temporal: 80% treino / 20% teste
    split    = int(len(df_model) * 0.8)
    X_train  = X.iloc[:split]
    X_test   = X.iloc[split:]
    y_train  = y.iloc[:split]
    y_test   = y.iloc[split:]
    df_test  = df_model.iloc[split:].reset_index(drop=True)

    print(f"  Treino: {len(X_train)} semanas | Teste: {len(X_test)} semanas")

    resultados = []

    # Regressão Linear — baseline
    lr, pred_lr, res_lr = avaliar_modelo(
        "Regressão Linear", LinearRegression(),
        X_train, X_test, y_train, y_test
    )
    resultados.append(res_lr)
    plotar_comparacao(df_test, None, "Regressão Linear", pred_lr)

    # Random Forest
    rf, pred_rf, res_rf = avaliar_modelo(
        "Random Forest",
        RandomForestRegressor(n_estimators=200, random_state=42),
        X_train, X_test, y_train, y_test
    )
    resultados.append(res_rf)
    plotar_comparacao(df_test, None, "Random Forest", pred_rf)

    # XGBoost — modelo principal
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

    # Salvar modelo XGBoost treinado
    os.makedirs("models", exist_ok=True)
    joblib.dump(xgb, "models/xgboost_dengue.pkl")
    joblib.dump(features, "models/features.pkl")
    print("\n✅ Modelo XGBoost salvo em models/")

    # ── 4. Gerar mapa por bairro ───────────────────────────
    print("\n🗺️  Etapa 4: Gerando mapa...")
    try:
        gerar_mapa_bairros(
            "data/geo/recife_bairros.geojson",
            "data/processed/dengue_processado.csv"
        )
    except Exception as e:
        print(f"  ⚠️ Mapa não gerado: {e}")

    # ── 5. Gerar relatório PowerPoint ──────────────────────
    print("\n📑 Etapa 5: Gerando PowerPoint...")
    try:
        gerar_ppt()
    except Exception as e:
        print(f"  ⚠️ PPT não gerado: {e}")

    print("\n✅ Pipeline finalizado!")
    print("   Outputs em: outputs/")
    print("   Modelo em:  models/xgboost_dengue.pkl")
    print("   API:        python src/api.py")
    print("   Dashboard:  python src/dashboard.py")


if __name__ == "__main__":
    main()