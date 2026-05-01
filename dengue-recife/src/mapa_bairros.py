import folium
import pandas as pd
import numpy as np
import json


def simular_bairros(df):
    bairros = [
        "Boa Viagem", "Casa Amarela", "Várzea", "Ibura",
        "Afogados", "Madalena", "Pina", "Imbiribeira",
        "Torre", "Graças"
    ]

    pesos = np.array([1.5, 1.2, 1.0, 1.4, 1.1, 0.9, 1.3, 1.2, 0.8, 1.0])
    pesos = pesos / pesos.sum()

    total_casos = df["casos"].sum()
    casos_bairro = (total_casos * pesos).astype(int)

    return pd.DataFrame({
        "bairro": bairros,
        "casos": casos_bairro
    })


def gerar_mapa_bairros(caminho_geojson, caminho_dados):
    df = pd.read_csv(caminho_dados)
    df_bairro = simular_bairros(df)

    # 🔥 alinhar nome com GeoJSON
    df_bairro.rename(columns={"bairro": "EBAIRRNOME"}, inplace=True)

    # ✅ ler geojson
    with open(caminho_geojson, encoding="utf-8") as f:
        geojson = json.load(f)

    mapa = folium.Map(location=[-8.05, -34.9], zoom_start=12)

    folium.Choropleth(
        geo_data=geojson,
        data=df_bairro,
        columns=["EBAIRRNOME", "casos"],
        key_on="feature.properties.EBAIRRNOME",
        fill_color="YlOrRd",
        legend_name="Casos estimados de dengue"
    ).add_to(mapa)

    mapa.save("outputs/mapa_bairros.html")

    print("🗺️ Mapa gerado!")