"""
🦟 DengueAlert Recife — API Flask
Serve previsões reais usando modelo XGBoost + mapa com dados reais por bairro
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import sys
import json
import glob

# ─── CONFIG ─────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH    = os.path.join(BASE_DIR, "models", "xgboost_dengue.pkl")
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

    model = XGBRegressor(n_estimators=200, learning_rate=0.05,
                         max_depth=5, random_state=42)
    model.fit(df[FEATURES], df['casos_est'])

    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(FEATURES, FEATURES_PATH)
    print("✅ Modelo treinado e salvo")
    return model, FEATURES


def carregar_modelo():
    if os.path.exists(MODEL_PATH):
        print("📦 Carregando modelo salvo...")
        return joblib.load(MODEL_PATH), joblib.load(FEATURES_PATH)
    return treinar_modelo()


modelo, FEATURES = carregar_modelo()

# ─── CLASSIFICAÇÃO DE RISCO (previsão semanal) ──────────
def classificar_risco(casos):
    if casos < 100:
        return {"nivel": "baixo",  "label": "🟢 Baixo",  "cor": "#2A7A4B",
                "gauge": 20, "mensagem": "Risco baixo. Manter ações preventivas."}
    elif casos < 400:
        return {"nivel": "medio",  "label": "🟡 Médio",  "cor": "#D97B2A",
                "gauge": 55, "mensagem": "Risco moderado. Intensificar ações."}
    else:
        return {"nivel": "alto",   "label": "🔴 Alto",   "cor": "#C8382A",
                "gauge": 90, "mensagem": "Alto risco. Ativar protocolo emergencial."}

# ─── DADOS REAIS POR BAIRRO (cache em memória) ──────────
_cache_bairros = None

def carregar_dados_bairros():
    """
    Lê os CSVs reais da Prefeitura do Recife (2013-2024),
    agrega casos confirmados por bairro e armazena em cache.
    Confirmados = CLASSI_FIN / tp_classificacao_final em {10, 11, 12}
    """
    global _cache_bairros
    if _cache_bairros is not None:
        return _cache_bairros

    pasta     = os.path.join(BASE_DIR, "data", "raw", "recife_bairros")
    arquivos  = sorted(glob.glob(os.path.join(pasta, "dengue*.csv")))
    CONFIRMADOS = {"10", "11", "12", "10.0", "11.0", "12.0"}
    frames = []

    for arq in arquivos:
        try:
            with open(arq, encoding="latin-1") as f:
                header = f.readline().strip().replace('"', '')
            sep     = ";" if header.count(";") > header.count(",") else ","
            colunas = [c.strip() for c in header.split(sep)]

            col_bairro  = "NM_BAIRRO"              if "NM_BAIRRO"              in colunas else "no_bairro_residencia"
            col_classif = "CLASSI_FIN"              if "CLASSI_FIN"             in colunas else "tp_classificacao_final"

            if col_bairro not in colunas or col_classif not in colunas:
                continue

            df = pd.read_csv(arq, sep=sep, dtype=str, encoding="latin-1",
                             usecols=[col_bairro, col_classif],
                             on_bad_lines="skip", quotechar='"')

            df[col_bairro]  = df[col_bairro].str.strip().str.strip('"')
            df[col_classif] = df[col_classif].str.strip().str.strip('"')

            df_conf = df[df[col_classif].isin(CONFIRMADOS)][[col_bairro]].copy()
            df_conf.columns = ["bairro"]
            frames.append(df_conf)
        except Exception:
            continue

    if not frames:
        _cache_bairros = {}
        return _cache_bairros

    df_total = pd.concat(frames, ignore_index=True)
    df_total["bairro"] = (
        df_total["bairro"].str.upper().str.strip()
        .str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")
    )
    df_total = df_total[df_total["bairro"].notna() & (df_total["bairro"] != "")]

    _cache_bairros = df_total.groupby("bairro").size().to_dict()
    total = sum(_cache_bairros.values())
    print(f"✅ Dados reais: {len(_cache_bairros)} bairros, {total:,} casos confirmados")
    return _cache_bairros

# ─── ROTAS ──────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({"status": "ok", "modelo": "XGBoost", "features": FEATURES})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON inválido"}), 400

        missing = [f for f in FEATURES if f not in data]
        if missing:
            return jsonify({"error": f"Faltando: {missing}"}), 400

        X    = pd.DataFrame([{f: float(data[f]) for f in FEATURES}])
        pred = max(0, round(float(modelo.predict(X)[0])))
        return jsonify({"casos_previstos": pred, "risco": classificar_risco(pred)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/historico")
def historico():
    try:
        path = os.path.join(BASE_DIR, "data", "processed", "dengue_processado.csv")
        df   = pd.read_csv(path)
        df["data"] = pd.to_datetime(df["data"])
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats")
def stats():
    try:
        path = os.path.join(BASE_DIR, "data", "processed", "dengue_processado.csv")
        df   = pd.read_csv(path)
        return jsonify({
            "total_casos": int(df["casos_est"].sum()),
            "media":       round(float(df["casos_est"].mean()), 1),
            "max":         int(df["casos_est"].max())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/mapa", methods=["GET"])
def mapa():
    """
    Retorna GeoJSON dos bairros de Recife com casos REAIS confirmados
    (fonte: Prefeitura do Recife, 2013-2024) e nível de risco histórico.

    Classificação por casos acumulados:
        0          → sem_dados  (#CCCCCC)
        < 300      → baixo      (#2A7A4B)
        300-1000   → medio      (#D97B2A)
        1000-2000  → alto       (#C8382A)
        > 2000     → critico    (#7B0000)
    """
    try:
        geo_path = os.path.join(BASE_DIR, "data", "geo", "recife_bairros.geojson")
        with open(geo_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        dados_bairros = carregar_dados_bairros()
        total_casos   = sum(dados_bairros.values()) if dados_bairros else 1

        for feature in geojson["features"]:
            props  = feature["properties"]
            bairro = props.get("EBAIRRNOME", "")

            # Normaliza nome para casar com os CSVs
            bairro_norm = (
                bairro.strip().upper()
                .encode("ascii", errors="ignore").decode("ascii")
            )
            props["BAIRRO_NORM"] = bairro_norm

            casos = dados_bairros.get(bairro_norm, 0)

            if casos == 0:
                nivel, cor, label = "sem_dados", "#CCCCCC", "⚪ Sem dados"
            elif casos < 300:
                nivel, cor, label = "baixo",    "#2A7A4B", "🟢 Baixo"
            elif casos < 1000:
                nivel, cor, label = "medio",    "#D97B2A", "🟡 Médio"
            elif casos < 2000:
                nivel, cor, label = "alto",     "#C8382A", "🔴 Alto"
            else:
                nivel, cor, label = "critico",  "#7B0000", "🔴 Crítico"

            props["bairro_nome"] = bairro
            props["casos"]       = casos
            props["risco"]       = nivel
            props["cor"]         = cor
            props["label"]       = label
            props["percentual"]  = round(casos / total_casos * 100, 2)

        return jsonify(geojson)

    except Exception as e:
        print("Erro no mapa:", e)
        return jsonify({"error": str(e)}), 500


# ─── RUN ────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🦟 DengueAlert API rodando:")
    print("👉 http://127.0.0.1:5000")
    print("👉 POST /predict   — previsão XGBoost")
    print("👉 GET  /historico — série temporal")
    print("👉 GET  /stats     — estatísticas")
    print("👉 GET  /mapa      — mapa com dados reais\n")
    app.run(debug=True, port=5000)