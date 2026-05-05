"""
src/mapa_bairros.py

Mapa coroplético de dengue por bairro de Recife com dados REAIS.
Fonte: http://dados.recife.pe.gov.br/dataset/casos-de-dengue-zika-e-chikungunya

Formatos identificados nos CSVs:
  2013:      sep=;  bairro=no_bairro_residencia  classif=tp_classificacao_final  confirmados=10,11,12
  2015-2020: sep=,  bairro=no_bairro_residencia  classif=tp_classificacao_final  confirmados=10,11,12
  2021-2024: sep=;  bairro=NM_BAIRRO             classif=CLASSI_FIN              confirmados=10,11,12

Tabela SINAN — CLASSI_FIN / tp_classificacao_final:
  5  = Descartado
  8  = Inconclusivo
  10 = Dengue confirmada
  11 = Dengue com sinais de alarme
  12 = Dengue grave
"""

import os, glob, json
import folium
import pandas as pd
from folium.plugins import Fullscreen

# Códigos confirmados em ambos os formatos (como string e float)
CONFIRMADOS = {"10", "11", "12", "10.0", "11.0", "12.0"}


def detectar_formato(arq: str) -> dict:
    """Detecta separador e nomes de colunas lendo o cabeçalho."""
    for enc in ("latin-1", "utf-8"):
        try:
            with open(arq, encoding=enc) as f:
                linha0 = f.readline().strip()
            break
        except Exception:
            continue

    header_limpo = linha0.replace('"', '')
    sep = ";" if header_limpo.count(";") > header_limpo.count(",") else ","
    colunas = [c.strip().strip('"') for c in header_limpo.split(sep)]

    # Coluna de bairro
    if "NM_BAIRRO" in colunas:
        col_bairro = "NM_BAIRRO"
    elif "no_bairro_residencia" in colunas:
        col_bairro = "no_bairro_residencia"
    else:
        candidates = [c for c in colunas if "bairro" in c.lower() and "infec" not in c.lower()]
        col_bairro = candidates[0] if candidates else None

    # Coluna de classificação
    if "CLASSI_FIN" in colunas:
        col_classif = "CLASSI_FIN"
    elif "tp_classificacao_final" in colunas:
        col_classif = "tp_classificacao_final"
    else:
        candidates = [c for c in colunas if "classif" in c.lower() or "classi" in c.lower()]
        col_classif = candidates[0] if candidates else None

    return {"sep": sep, "bairro": col_bairro, "classif": col_classif}


def carregar_csvs_reais(pasta: str = "data/raw/recife_bairros") -> pd.DataFrame:
    arquivos = sorted(glob.glob(os.path.join(pasta, "dengue*.csv")))

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo em '{pasta}'.\n"
            "Baixe em: http://dados.recife.pe.gov.br/dataset/casos-de-dengue-zika-e-chikungunya"
        )

    print(f"Arquivos encontrados: {len(arquivos)}\n")
    frames = []

    for arq in arquivos:
        nome = os.path.basename(arq)
        fmt  = detectar_formato(arq)

        if not fmt["bairro"] or not fmt["classif"]:
            print(f"  {nome}... AVISO: colunas não identificadas — pulando")
            continue

        print(f"  {nome} [sep='{fmt['sep']}' classif='{fmt['classif']}']...", end=" ")

        try:
            df = pd.read_csv(
                arq,
                sep=fmt["sep"],
                dtype=str,
                encoding="latin-1",
                usecols=[fmt["bairro"], fmt["classif"]],
                on_bad_lines="skip",
                quotechar='"',
            )

            df[fmt["bairro"]]  = df[fmt["bairro"]].str.strip().str.strip('"')
            df[fmt["classif"]] = df[fmt["classif"]].str.strip().str.strip('"')

            # Filtra confirmados (códigos 10, 11, 12)
            df_conf = df[df[fmt["classif"]].isin(CONFIRMADOS)][[fmt["bairro"]]].copy()
            df_conf.columns = ["bairro"]
            frames.append(df_conf)
            print(f"OK  {len(df_conf):,} casos confirmados")

        except Exception as e:
            print(f"ERRO: {e}")

    if not frames:
        raise ValueError("Nenhum dado válido carregado.")

    df_total = pd.concat(frames, ignore_index=True)

    # Normaliza: maiúsculas, remove acentos
    df_total["bairro"] = (
        df_total["bairro"]
        .str.upper().str.strip()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("ascii")
    )
    df_total = df_total[df_total["bairro"].notna() & (df_total["bairro"] != "")]

    resumo = (
        df_total.groupby("bairro").size()
        .reset_index(name="casos")
        .sort_values("casos", ascending=False)
        .reset_index(drop=True)
    )

    print(f"\nTotal: {resumo['casos'].sum():,} casos confirmados em {len(resumo)} bairros")
    print("\nTop 10 bairros:")
    print(resumo.head(10).to_string(index=False))
    return resumo


def gerar_mapa_bairros(
    caminho_geojson: str = "data/geo/recife_bairros.geojson",
    pasta_csvs:      str = "data/raw/recife_bairros",
    caminho_saida:   str = "outputs/mapa_bairros.html",
):
    df_bairros = carregar_csvs_reais(pasta_csvs)

    with open(caminho_geojson, encoding="utf-8") as f:
        geojson = json.load(f)

    for feat in geojson["features"]:
        nome = feat["properties"].get("EBAIRRNOME", "")
        feat["properties"]["BAIRRO_NORM"] = (
            nome.strip().upper()
            .encode("ascii", errors="ignore").decode("ascii")
        )

    mapa = folium.Map(
        location=[-8.05, -34.90],
        zoom_start=12,
        tiles="CartoDB positron",
    )
    Fullscreen().add_to(mapa)

    folium.Choropleth(
        geo_data=geojson,
        data=df_bairros,
        columns=["bairro", "casos"],
        key_on="feature.properties.BAIRRO_NORM",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.4,
        legend_name="Casos confirmados de dengue (2013-2024)",
        nan_fill_color="#DDDDDD",
        nan_fill_opacity=0.3,
        highlight=True,
    ).add_to(mapa)

    folium.GeoJson(
        geojson,
        style_function=lambda x: {"fillOpacity": 0, "weight": 0},
        tooltip=folium.GeoJsonTooltip(
            fields=["BAIRRO_NORM"], aliases=["Bairro:"]
        ),
    ).add_to(mapa)

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    mapa.save(caminho_saida)
    print(f"\n🗺️  Mapa salvo: {caminho_saida} ({os.path.getsize(caminho_saida)//1024} KB)")
    print(f"   Bairros com dados reais: {len(df_bairros)}")


if __name__ == "__main__":
    gerar_mapa_bairros()