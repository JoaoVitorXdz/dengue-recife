from pptx import Presentation
from pptx.util import Inches
import os

OUTPUT_DIR = "outputs"

def add_slide(prs, titulo, imagem=None):
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = titulo

    if imagem:
        imagem = os.path.abspath(imagem)

        print(f"🔍 Verificando imagem: {imagem}")

        if not os.path.exists(imagem):
            print(f"⚠️ Imagem não encontrada: {imagem}")
            return

        if os.path.getsize(imagem) < 1000:
            print(f"⚠️ Imagem inválida/vazia: {imagem}")
            return

        slide.shapes.add_picture(imagem, Inches(1), Inches(2), width=Inches(6))
        print("✅ Imagem adicionada")

def gerar_ppt():
    prs = Presentation()

    add_slide(prs, "Análise de Dengue em Recife")
    add_slide(prs, "Casos ao longo do tempo", f"{OUTPUT_DIR}/casos_ao_longo_do_tempo.png")
    add_slide(prs, "Correlação", f"{OUTPUT_DIR}/correlacao.png")
    add_slide(prs, "Importância das Variáveis", f"{OUTPUT_DIR}/importancia_features.png")
    add_slide(prs, "Previsão XGBoost", f"{OUTPUT_DIR}/previsao_xgboost.png")

    prs.save("relatorio_dengue_recife.pptx")
    print("📊 PPT gerado com sucesso!")

if __name__ == "__main__":
    gerar_ppt()