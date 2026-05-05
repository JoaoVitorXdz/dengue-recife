"""
src/visualization.py
Centraliza todas as funções de geração de gráficos do projeto.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

OUTPUT_DIR = "outputs"


def _salvar(caminho: str):
    """Salva a figura atual, valida o arquivo e fecha."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()

    if not os.path.exists(caminho):
        raise RuntimeError(f"Imagem não foi criada: {caminho}")
    if os.path.getsize(caminho) < 1000:
        raise RuntimeError(f"Imagem criada mas está vazia: {caminho}")

    print(f"  ✅ {caminho}")


# ─── EDA ────────────────────────────────────────────────────────────────────

def gerar_grafico_casos(df: pd.DataFrame):
    """Série temporal de casos ao longo do tempo."""
    df = df.sort_values("data")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df["data"], df["casos_est"], color="crimson", linewidth=1.5)
    ax.fill_between(df["data"], df["casos_est"], alpha=0.08, color="crimson")
    ax.set_title("Casos estimados de dengue em Recife (2015–2024)", fontsize=13)
    ax.set_xlabel("Data")
    ax.set_ylabel("Casos estimados")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    _salvar(f"{OUTPUT_DIR}/casos_ao_longo_do_tempo.png")


def gerar_grafico_niveis(df: pd.DataFrame):
    """Distribuição das semanas por nível de alerta epidemiológico."""
    contagem = df["nivel"].value_counts().sort_index()
    cores    = {1: "#2A7A4B", 2: "#D4C420", 3: "#D97B2A", 4: "#C8382A"}
    labels   = {1: "1 — Verde", 2: "2 — Amarelo", 3: "3 — Laranja", 4: "4 — Vermelho"}

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(
        [labels.get(n, n) for n in contagem.index],
        contagem.values,
        color=[cores.get(n, "gray") for n in contagem.index],
        edgecolor="white", linewidth=0.5
    )
    for bar, val in zip(bars, contagem.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                str(val), ha="center", va="bottom", fontsize=9)

    ax.set_title("Distribuição dos níveis de alerta", fontsize=13)
    ax.set_xlabel("Nível de alerta")
    ax.set_ylabel("Semanas")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    _salvar(f"{OUTPUT_DIR}/niveis_alerta.png")


def gerar_grafico_sazonalidade(df: pd.DataFrame):
    """Média de casos por mês — sazonalidade anual."""
    meses  = range(1, 13)
    nomes  = ["Jan","Fev","Mar","Abr","Mai","Jun",
              "Jul","Ago","Set","Out","Nov","Dez"]
    medias = [df[df["mes"] == m]["casos_est"].mean() for m in meses]
    cores  = ["#C8382A" if v > 400 else "#D97B2A" if v > 200 else "#2A7A4B"
              for v in medias]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(nomes, medias, color=cores, edgecolor="white", linewidth=0.5)
    ax.set_title("Sazonalidade — média de casos por mês", fontsize=13)
    ax.set_xlabel("Mês")
    ax.set_ylabel("Média de casos")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    _salvar(f"{OUTPUT_DIR}/sazonalidade_mensal.png")


# ─── MODELAGEM ──────────────────────────────────────────────────────────────

def plotar_comparacao(df_test: pd.DataFrame, nome_modelo: str, y_pred):
    """Gráfico real vs previsto para um modelo."""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df_test["data"].values, df_test["casos_est"].values,
            label="Real", color="crimson", linewidth=1.5)
    ax.plot(df_test["data"].values, y_pred,
            label=f"Previsto ({nome_modelo})", color="steelblue",
            linewidth=1.5, linestyle="--")
    ax.set_title(f"Previsão de casos de dengue — {nome_modelo}", fontsize=13)
    ax.set_xlabel("Data")
    ax.set_ylabel("Casos estimados")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    fname = f"{OUTPUT_DIR}/previsao_{nome_modelo.lower().replace(' ', '_')}.png"
    _salvar(fname)


def plotar_importancia(modelo, features: list):
    """Importância das features — XGBoost."""
    importancias = pd.Series(modelo.feature_importances_, index=features)
    importancias = importancias.sort_values()

    cores = ["#C8382A" if v > 0.15 else "#D97B2A" if v > 0.05 else "#6B9BB5"
             for v in importancias.values]

    fig, ax = plt.subplots(figsize=(8, 5))
    importancias.plot(kind="barh", ax=ax, color=cores)
    ax.set_title("Importância das features — XGBoost", fontsize=13)
    ax.set_xlabel("Importância relativa")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()

    _salvar(f"{OUTPUT_DIR}/importancia_features.png")


def plotar_comparativo_modelos(resultados: list):
    """
    Gráfico comparativo de MAE e R² entre os modelos avaliados.

    Parâmetro:
        resultados: lista de dicts com chaves 'nome', 'MAE', 'RMSE', 'R2'
    """
    df_res = pd.DataFrame(resultados)
    nomes  = df_res["nome"].tolist()
    cores  = ["#6B5E58", "#D97B2A", "#C8382A"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    for ax, metrica, label in zip(
        axes,
        ["MAE", "RMSE", "R2"],
        ["MAE (casos)", "RMSE (casos)", "R²"]
    ):
        bars = ax.bar(nomes, df_res[metrica], color=cores,
                      edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, df_res[metrica]):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.003 * max(df_res[metrica]),
                    f"{val:.3f}", ha="center", va="bottom", fontsize=9)
        ax.set_title(label, fontsize=11)
        ax.set_xticklabels(nomes, rotation=12, ha="right", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle("Comparativo entre modelos", fontsize=13, y=1.02)
    plt.tight_layout()

    _salvar(f"{OUTPUT_DIR}/comparativo_modelos.png")