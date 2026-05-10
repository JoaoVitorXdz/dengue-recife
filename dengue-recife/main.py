from src.processing import carregar_e_processar, salvar_processado
from src.visualization import (
    gerar_grafico_casos,
    gerar_grafico_niveis,
    gerar_grafico_sazonalidade,
    plotar_comparativo_modelos,
)
from src.mapa_bairros import gerar_mapa_bairros
from src.report import gerar_ppt
from src.model import (
    carregar_dados,
    preparar_features,
    avaliar_modelo,
    validacao_cruzada,
    plotar_comparacao,
    plotar_importancia,
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
    print("\n📊 Etapa 2: Gerando gráficos EDA...")
    gerar_grafico_casos(df)
    gerar_grafico_niveis(df)
    gerar_grafico_sazonalidade(df)

    # ── 3. Treinar e avaliar modelos ML ────────────────────
    print("\n🤖 Etapa 3: Treinando modelos...")
    df_model = carregar_dados()
    X, y, features = preparar_features(df_model)

    # Split temporal: 80% treino / 20% teste
    split   = int(len(df_model) * 0.8)
    X_train = X.iloc[:split];  X_test = X.iloc[split:]
    y_train = y.iloc[:split];  y_test = y.iloc[split:]
    df_test = df_model.iloc[split:].reset_index(drop=True)

    print(f"  Treino: {len(X_train)} semanas | Teste: {len(X_test)} semanas")

    modelos = [
        ("Regressão Linear", LinearRegression()),
        ("Random Forest",    RandomForestRegressor(n_estimators=200, random_state=42)),
        ("XGBoost",          XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42)),
    ]

    resultados = []
    xgb_fit    = None

    for nome, estimador in modelos:
        # Avaliação no conjunto de teste
        modelo_fit, y_pred, res = avaliar_modelo(
            nome, estimador, X_train, X_test, y_train, y_test
        )

        # Validação cruzada 5-fold temporal
        cv = validacao_cruzada(nome, estimador, X, y)
        res.update(cv)
        resultados.append(res)

        # Gráfico real vs previsto
        plotar_comparacao(df_test, None, nome, y_pred)

        if nome == "XGBoost":
            xgb_fit = modelo_fit

    # Importância das features (XGBoost)
    plotar_importancia(xgb_fit, features)

    # Gráfico comparativo dos 3 modelos
    plotar_comparativo_modelos(resultados)

    # Tabela comparativa
    print("\n=== COMPARATIVO FINAL ===")
    cols = ["nome", "MAE", "RMSE", "R2", "cv_r2_mean", "cv_r2_std", "cv_mae"]
    print(pd.DataFrame(resultados)[cols].to_string(index=False))

    # Salvar modelo XGBoost treinado
    os.makedirs("models", exist_ok=True)
    joblib.dump(xgb_fit,  "models/xgboost_dengue.pkl")
    joblib.dump(features, "models/features.pkl")
    print("\n✅ Modelo XGBoost salvo em models/")

    # ── 4. Gerar mapa por bairro ───────────────────────────
    print("\n🗺️  Etapa 4: Gerando mapa...")
    try:
        gerar_mapa_bairros(
            "data/geo/recife_bairros.geojson",
            "data/raw/recife_bairros",
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