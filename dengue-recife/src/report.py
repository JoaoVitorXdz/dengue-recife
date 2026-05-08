"""
src/report.py
Gera relatório PowerPoint completo com todos os gráficos do projeto.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

OUTPUT_DIR = "outputs"

# ── CORES ────────────────────────────────────────────────
RED   = RGBColor(0xC8, 0x38, 0x2A)
DARK  = RGBColor(0x1A, 0x14, 0x10)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY  = RGBColor(0x6B, 0x5E, 0x58)
PAPER = RGBColor(0xFA, 0xF7, 0xF4)


def set_bg(slide, r, g, b):
    """Define a cor de fundo do slide."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)


def add_text_box(slide, text, left, top, width, height,
                 size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    return txBox


def add_rect(slide, left, top, width, height, r, g, b):
    from pptx.util import Inches
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(r, g, b)
    shape.line.fill.background()
    return shape


def add_image_safe(slide, path, left, top, width=None, height=None):
    """Adiciona imagem ao slide com verificação de existência."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        print(f"  ⚠️  Imagem não encontrada: {abs_path}")
        return False
    if os.path.getsize(abs_path) < 1000:
        print(f"  ⚠️  Imagem inválida: {abs_path}")
        return False
    try:
        kwargs = {"left": Inches(left), "top": Inches(top)}
        if width:  kwargs["width"]  = Inches(width)
        if height: kwargs["height"] = Inches(height)
        slide.shapes.add_picture(abs_path, **kwargs)
        print(f"  ✅  {os.path.basename(abs_path)}")
        return True
    except Exception as e:
        print(f"  ❌  Erro ao adicionar {path}: {e}")
        return False


def slide_capa(prs):
    """Slide 1 — Capa."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(slide, 0x1A, 0x14, 0x10)

    # Barra vermelha esquerda
    add_rect(slide, 0, 0, 0.12, 7.5, 0xC8, 0x38, 0x2A)

    # Título
    add_text_box(slide, "DengueAlert", 0.4, 1.2, 9, 1.2,
                 size=48, bold=True, color=WHITE)
    add_text_box(slide, "Recife", 0.4, 2.2, 9, 1.0,
                 size=48, bold=True, color=RGBColor(0xC8, 0x38, 0x2A))
    add_text_box(slide,
                 "Previsão de casos de dengue com Machine Learning e dados reais",
                 0.4, 3.3, 9.0, 0.8, size=16, color=RGBColor(0xCC, 0xBB, 0xBB))

    # Linha
    add_rect(slide, 0.4, 4.3, 9.2, 0.03, 0x44, 0x38, 0x35)

    # Rodapé
    add_text_box(slide,
                 "Faculdade Estácio  ·  João Vitor  ·  2025",
                 0.4, 4.5, 9.0, 0.5, size=12,
                 color=RGBColor(0x99, 0x88, 0x88))


def slide_secao(prs, titulo, subtitulo=""):
    """Slide divisor de seção."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, 0xC8, 0x38, 0x2A)
    add_rect(slide, 0, 0, 0.12, 7.5, 0xAA, 0x28, 0x1C)
    add_text_box(slide, titulo, 0.5, 2.5, 9.0, 1.2,
                 size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    if subtitulo:
        add_text_box(slide, subtitulo, 0.5, 3.6, 9.0, 0.6,
                     size=14, color=RGBColor(0xFF, 0xCC, 0xCC),
                     align=PP_ALIGN.CENTER)


def slide_grafico(prs, titulo, subtitulo, img_path,
                  img_left=0.5, img_top=1.6, img_w=9.0):
    """Slide com título + gráfico."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, 0xFA, 0xF7, 0xF4)

    # Faixa topo
    add_rect(slide, 0, 0, 10, 0.08, 0xC8, 0x38, 0x2A)

    # Título e subtítulo
    add_text_box(slide, titulo, 0.4, 0.18, 9, 0.6,
                 size=22, bold=True, color=DARK)
    if subtitulo:
        add_text_box(slide, subtitulo, 0.4, 0.75, 9, 0.4,
                     size=12, color=GRAY)

    add_image_safe(slide, img_path, img_left, img_top, width=img_w)


def slide_dois_graficos(prs, titulo, subtitulo, img1, img2,
                        titulo1="", titulo2=""):
    """Slide com dois gráficos lado a lado."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, 0xFA, 0xF7, 0xF4)
    add_rect(slide, 0, 0, 10, 0.08, 0xC8, 0x38, 0x2A)
    add_text_box(slide, titulo, 0.4, 0.18, 9, 0.6,
                 size=22, bold=True, color=DARK)
    if subtitulo:
        add_text_box(slide, subtitulo, 0.4, 0.75, 9, 0.4,
                     size=12, color=GRAY)
    if titulo1:
        add_text_box(slide, titulo1, 0.4, 1.3, 4.5, 0.3,
                     size=11, bold=True, color=GRAY)
    if titulo2:
        add_text_box(slide, titulo2, 5.1, 1.3, 4.5, 0.3,
                     size=11, bold=True, color=GRAY)
    add_image_safe(slide, img1, 0.3, 1.6, width=4.5)
    add_image_safe(slide, img2, 5.0, 1.6, width=4.7)


def slide_resultados(prs):
    """Slide de tabela de resultados dos modelos."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, 0xFA, 0xF7, 0xF4)
    add_rect(slide, 0, 0, 10, 0.08, 0xC8, 0x38, 0x2A)
    add_text_box(slide, "Resultados dos Modelos ML",
                 0.4, 0.18, 9, 0.6, size=22, bold=True, color=DARK)
    add_text_box(slide, "Split temporal 80/20 · Validação cruzada 5-fold",
                 0.4, 0.75, 9, 0.4, size=12, color=GRAY)

    # Tabela
    from pptx.util import Inches, Pt
    rows, cols = 4, 5
    table = slide.shapes.add_table(
        rows, cols,
        Inches(0.3), Inches(1.4),
        Inches(9.4), Inches(2.8)
    ).table

    headers = ["Modelo", "MAE", "RMSE", "R²", "CV R² médio"]
    data    = [
        ["Regressão Linear", "21.9", "30.6", "0.976", "0.891"],
        ["Random Forest",    "17.5", "41.0", "0.958", "0.877"],
        ["XGBoost ★",        "14.3", "38.1", "0.964", "0.876"],
    ]

    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RED
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.bold  = True
        run.font.color.rgb = WHITE
        run.font.size  = Pt(13)

    for ri, row in enumerate(data):
        is_xgb = ri == 2
        for ci, val in enumerate(row):
            cell = table.cell(ri + 1, ci)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xFF, 0xF3, 0xF2) if is_xgb
                else (WHITE if ri % 2 == 0 else RGBColor(0xFA, 0xF7, 0xF4))
            )
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            run = p.runs[0]
            run.font.size = Pt(13)
            run.font.bold = is_xgb and ci == 1
            run.font.color.rgb = RED if (is_xgb and ci == 1) else DARK

    # Insight
    add_rect(slide, 0.3, 4.4, 9.4, 0.06, 0xC8, 0x38, 0x2A)
    add_rect(slide, 0.3, 4.55, 9.4, 1.2,
             0xFF, 0xFF, 0xFF)
    add_rect(slide, 0.3, 4.55, 0.07, 1.2, 0xC8, 0x38, 0x2A)
    add_text_box(slide,
                 "💡  XGBoost erra em média apenas 14,3 casos/semana. "
                 "Os lag features (casos anteriores) respondem por mais de 70% "
                 "da importância do modelo, confirmando forte autocorrelação temporal.",
                 0.5, 4.65, 9.0, 1.0, size=12, color=GRAY)


def slide_conclusao(prs):
    """Slide final de conclusão."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, 0xC8, 0x38, 0x2A)
    add_rect(slide, 0, 0, 0.12, 7.5, 0xAA, 0x28, 0x1C)

    add_text_box(slide, "🦟", 0.3, 0.3, 1.5, 1.5, size=60)
    add_text_box(slide, "Conclusão", 0.4, 1.5, 9, 0.9,
                 size=36, bold=True, color=WHITE)

    bullets = [
        "R² acima de 0.96 — alta precisão preditiva",
        "51.429 casos reais confirmados da Prefeitura do Recife",
        "Sistema completo: ingestão → ML → API → frontend → mapa",
        "Potencial real de apoio à Vigilância Epidemiológica",
    ]
    for i, b in enumerate(bullets):
        add_rect(slide, 0.4, 2.55 + i * 0.72, 0.12, 0.12,
                 0xFF, 0xFF, 0xFF)
        add_text_box(slide, b, 0.65, 2.48 + i * 0.72, 9.0, 0.5,
                     size=14, color=WHITE)

    add_rect(slide, 0, 6.8, 10, 0.7, 0xAA, 0x28, 0x1C)
    add_text_box(slide,
                 "github.com/JoaoVitorXdz/dengue-recife  ·  Faculdade Estácio  ·  João Vitor  ·  2025",
                 0.3, 6.85, 9.4, 0.5, size=11,
                 color=RGBColor(0xFF, 0xCC, 0xCC),
                 align=PP_ALIGN.CENTER)


# ── PIPELINE PRINCIPAL ───────────────────────────────────

def gerar_ppt(saida: str = "relatorio_dengue_recife.pptx"):
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)

    print("\n📊 Gerando relatório PowerPoint...\n")

    # 1. Capa
    print("Slide 1 — Capa")
    slide_capa(prs)

    # 2. Seção: Dados
    print("Slide 2 — Seção Dados")
    slide_secao(prs, "01. Base de Dados",
                "520 semanas · 51.429 casos reais · 94 bairros de Recife")

    # 3. Casos ao longo do tempo
    print("Slide 3 — Casos ao longo do tempo")
    slide_grafico(prs,
                  "Casos estimados de dengue — Recife (2015–2024)",
                  "Série temporal semanal com picos sazonais claros",
                  f"{OUTPUT_DIR}/casos_ao_longo_do_tempo.png")

    # 4. Sazonalidade + Níveis de alerta
    print("Slide 4 — Sazonalidade e Níveis de alerta")
    slide_dois_graficos(prs,
                        "Sazonalidade e Distribuição de Alertas",
                        "Padrão mensal e semanas por nível epidemiológico",
                        f"{OUTPUT_DIR}/sazonalidade_mensal.png",
                        f"{OUTPUT_DIR}/niveis_alerta.png",
                        "Média de casos por mês",
                        "Níveis de alerta (1=verde … 4=vermelho)")

    # 5. Seção: Modelagem
    print("Slide 5 — Seção Modelagem")
    slide_secao(prs, "02. Machine Learning",
                "Regressão Linear · Random Forest · XGBoost + Cross-validation")

    # 6. Correlação
    print("Slide 6 — Correlação")
    slide_grafico(prs,
                  "Correlação: Temperatura, Umidade e Casos",
                  "Dispersão semanal — pares de variáveis climáticas vs casos",
                  f"{OUTPUT_DIR}/correlacao.png")

    # 7. Resultados (tabela)
    print("Slide 7 — Tabela de resultados")
    slide_resultados(prs)

    # 8. Comparativo dos modelos
    print("Slide 8 — Comparativo dos modelos")
    slide_grafico(prs,
                  "Comparativo MAE, RMSE e R² — 3 Modelos",
                  "XGBoost obteve menor MAE (14,3 casos/semana)",
                  f"{OUTPUT_DIR}/comparativo_modelos.png")

    # 9. Importância das features
    print("Slide 9 — Importância das features")
    slide_grafico(prs,
                  "Importância das Features — XGBoost",
                  "Lag features dominam: casos das semanas anteriores explicam >70% do modelo",
                  f"{OUTPUT_DIR}/importancia_features.png")

    # 10. Previsões dos modelos
    print("Slide 10 — Previsão Regressão Linear")
    slide_grafico(prs,
                  "Previsão vs Real — Regressão Linear",
                  "Baseline — R² = 0.976 · MAE = 21.9 casos/semana",
                  f"{OUTPUT_DIR}/previsao_regressao_linear.png")

    print("Slide 11 — Previsão Random Forest")
    slide_grafico(prs,
                  "Previsão vs Real — Random Forest",
                  "200 estimadores — R² = 0.958 · MAE = 17.5 casos/semana",
                  f"{OUTPUT_DIR}/previsao_random_forest.png")

    print("Slide 12 — Previsão XGBoost")
    slide_grafico(prs,
                  "Previsão vs Real — XGBoost ★",
                  "Melhor modelo — R² = 0.964 · MAE = 14.3 casos/semana",
                  f"{OUTPUT_DIR}/previsao_xgboost.png")

    # 13. Conclusão
    print("Slide 13 — Conclusão")
    slide_conclusao(prs)

    prs.save(saida)
    print(f"\n✅ Relatório salvo: {saida}")
    print(f"   Total de slides: {len(prs.slides)}")


if __name__ == "__main__":
    gerar_ppt()