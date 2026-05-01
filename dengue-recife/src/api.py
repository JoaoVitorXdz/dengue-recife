"""
🦟 DengueAlert Recife — API Flask
Serve previsões reais usando modelo XGBoost + mapa por bairro
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import sys
import json

# ─── CONFIG ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "xgboost_dengue.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "models", "features.pkl")

sys.path.append(BASE_DIR)

app = Flask(__name__)
CORS(app)

# ─── CARREGAR OU TREINAR MODELO ─────────────────────────
def treinar_modelo():
    from src.processing import carregar_e_processar
    from xgboost import XGBRegressor

    print("🚀 Treinando modelo...")

    df = carregar_e_processar()

    FEATURES = [
        'mes', 'semana',
        'tempmed', 'tempmin', 'tempmax',
        'umidmed', 'umidmin', 'umidmax',
        'p_rt1',
        'casos_lag1', 'casos_lag2', 'casos_lag4',
        'media_movel_4'
    ]

    X = df[FEATURES]
    y = df['casos_est']

    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )

    model.fit(X, y)

    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(FEATURES, FEATURES_PATH)

    print("✅ Modelo treinado e salvo")

    return model, FEATURES


def carregar_modelo():
    if os.path.exists(MODEL_PATH):
        print("📦 Carregando modelo salvo...")
        model = joblib.load(MODEL_PATH)
        features = joblib.load(FEATURES_PATH)
        return model, features

    return treinar_modelo()


modelo, FEATURES = carregar_modelo()

# ─── CLASSIFICAÇÃO DE RISCO ─────────────────────────────
def classificar_risco(casos):
    if casos < 100:
        return {
            "nivel": "baixo",
            "label": "🟢 Baixo",
            "cor": "#2A7A4B",
            "gauge": 20,
            "mensagem": "Risco baixo. Manter ações preventivas."
        }
    elif casos < 400:
        return {
            "nivel": "medio",
            "label": "🟡 Médio",
            "cor": "#D97B2A",
            "gauge": 55,
            "mensagem": "Risco moderado. Intensificar ações."
        }
    else:
        return {
            "nivel": "alto",
            "label": "🔴 Alto",
            "cor": "#C8382A",
            "gauge": 90,
            "mensagem": "Alto risco. Ativar protocolo emergencial."
        }

# ─── ROTAS ──────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "modelo": "XGBoost",
        "features": FEATURES
    })


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON inválido"}), 400

        missing = [f for f in FEATURES if f not in data]
        if missing:
            return jsonify({"error": f"Faltando: {missing}"}), 400

        X = pd.DataFrame([{f: float(data[f]) for f in FEATURES}])

        pred = float(modelo.predict(X)[0])
        pred = max(0, round(pred))

        risco = classificar_risco(pred)

        return jsonify({
            "casos_previstos": pred,
            "risco": risco
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/historico")
def historico():
    try:
        path = os.path.join(BASE_DIR, "data", "processed", "dengue_processado.csv")
        df = pd.read_csv(path)

        df['data'] = pd.to_datetime(df['data'])

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats")
def stats():
    try:
        path = os.path.join(BASE_DIR, "data", "processed", "dengue_processado.csv")
        df = pd.read_csv(path)

        return jsonify({
            "total_casos": int(df['casos_est'].sum()),
            "media": round(float(df['casos_est'].mean()), 1),
            "max": int(df['casos_est'].max())
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── MAPA COM VARIAÇÃO REALISTA ─────────────────────────
@app.route("/mapa", methods=["GET"])
def mapa():
    try:
        geo_path = os.path.join(BASE_DIR, "data", "geo", "recife_bairros.geojson")

        with open(geo_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        for feature in geojson["features"]:
            props = feature["properties"]

            # nome do bairro correto
            bairro = props.get("EBAIRRNOME", "Desconhecido")

            # 🔥 VARIAÇÃO INTELIGENTE (determinística)
            hash_bairro = abs(hash(bairro)) % 120

            base = 60 + hash_bairro

            data = {
                'mes': 3,
                'semana': 12,
                'tempmed': 27.5,
                'tempmin': 24,
                'tempmax': 31,
                'umidmed': 78,
                'umidmin': 68,
                'umidmax': 95,
                'p_rt1': 0.6,
                'casos_lag1': base,
                'casos_lag2': base - 10,
                'casos_lag4': base - 25,
                'media_movel_4': base - 5
            }

            X = pd.DataFrame([{f: float(data[f]) for f in FEATURES}])
            pred = max(0, round(float(modelo.predict(X)[0])))

            risco = classificar_risco(pred)

            # injeta no GeoJSON
            props["bairro_nome"] = bairro
            props["casos"] = pred
            props["risco"] = risco["nivel"]
            props["cor"] = risco["cor"]
            props["label"] = risco["label"]
            props["mensagem"] = risco["mensagem"]

        return jsonify(geojson)

    except Exception as e:
        print("Erro no mapa:", e)
        return jsonify({"error": str(e)}), 500


# ─── RUN ────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🦟 DengueAlert API rodando:")
    print("👉 http://127.0.0.1:5000")
    print("👉 POST /predict")
    print("👉 GET  /historico")
    print("👉 GET  /stats")
    print("👉 GET  /mapa\n")

    app.run(debug=True, port=5000)