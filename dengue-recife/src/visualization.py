import matplotlib.pyplot as plt

def gerar_grafico_casos(df):
    df = df.sort_values("data")

    plt.figure(figsize=(10,5))

    plt.plot(df["data"], df["casos"], linewidth=2)

    plt.title("Casos ao longo do tempo")
    plt.xlabel("Data")
    plt.ylabel("Casos")
    plt.grid(True)

    caminho = "outputs/casos_ao_longo_do_tempo.png"

    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()

    # 🔥 validação forte
    import os
    if not os.path.exists(caminho):
        raise Exception("Imagem NÃO foi criada")

    if os.path.getsize(caminho) < 1000:
        raise Exception("Imagem criada mas está vazia/corrompida")

    print(f"✅ Gráfico OK: {caminho}")