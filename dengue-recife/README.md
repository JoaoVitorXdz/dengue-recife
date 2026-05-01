# 🦟 Previsão de Casos de Dengue em Recife

Projeto de Big Data desenvolvido em Python para prever casos de dengue
em Recife (PE) com base em dados epidemiológicos e climáticos.

## 📋 Sobre o Projeto

A dengue é um problema de saúde pública grave em Recife, com picos
recorrentes todo ano. Este projeto utiliza técnicas de Machine Learning
para prever o número de casos estimados por semana epidemiológica,
permitindo antecipar surtos e auxiliar na tomada de decisão da
Vigilância Epidemiológica.

## 🎯 Objetivos

- Coletar e processar dados históricos de dengue (2015–2024)
- Identificar padrões sazonais e correlações climáticas
- Comparar modelos de ML para previsão de casos
- Apresentar resultados em dashboard interativo

## 📊 Resultados dos Modelos

| Modelo            | MAE        | RMSE       | R²    |
|-------------------|------------|------------|-------|
| Regressão Linear  | 21.9 casos | 30.6 casos | 0.976 |
| Random Forest     | 17.5 casos | 41.0 casos | 0.958 |
| XGBoost           | 14.3 casos | 38.1 casos | 0.964 |

> **Melhor modelo:** XGBoost com MAE de 14.3 casos/semana

## 🗂️ Estrutura do Projeto

```
dengue-recife/
├── data/
│   ├── raw/                  # Dados brutos da API InfoDengue
│   ├── processed/            # Dados processados com features
│   ├── external/             # Dados externos complementares
│   └── geo/                  # Shapefiles e GeoJSON dos bairros
├── frontend/
│   ├── index.html            # Landing page
│   ├── dashboard.html        # Dashboard interativo
│   ├── previsao.html         # Tela de previsão de risco
│   └── mapa.html             # Mapa por bairro
├── models/
│   ├── xgboost_dengue.pkl    # Modelo XGBoost treinado
│   └── features.pkl          # Lista de features do modelo
├── notebooks/
│   ├── 01_eda.ipynb          # Análise exploratória
│   └── 02_modelagem.ipynb    # Conclusões e modelagem
├── outputs/                  # Gráficos e relatórios gerados
├── src/
│   ├── api.py                # API Flask (serve o modelo)
│   ├── dashboard.py          # Dashboard Plotly Dash
│   ├── ingestion.py          # Coleta de dados InfoDengue
│   ├── mapa_bairros.py       # Mapa coroplético Folium
│   ├── model.py              # Treinamento e avaliação dos modelos
│   ├── processing.py         # Pré-processamento e feature engineering
│   ├── report.py             # Geração de relatório PowerPoint
│   └── visualization.py     # Geração de gráficos
├── main.py                   # Pipeline completo
├── requirements.txt
└── README.md
```

## 🔧 Tecnologias

- **Python 3.12**
- **Pandas / Dask** — manipulação de dados
- **Scikit-learn / XGBoost** — modelagem
- **Flask / Flask-CORS** — API REST
- **Plotly Dash** — dashboard interativo
- **Folium** — mapas geoespaciais
- **Matplotlib / Seaborn** — visualizações
- **python-pptx** — geração de relatório PowerPoint

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/JoaoVitorXdz/dengue-recife.git
cd dengue-recife

# Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows

# Instale as dependências
pip install -r requirements.txt
```

## ▶️ Como Executar

```bash
# 1. Coletar dados
python src/ingestion.py

# 2. Processar dados
python src/processing.py

# 3. Treinar modelos
python src/model.py

# 4. Rodar dashboard Dash
python src/dashboard.py
# Acesse: http://127.0.0.1:8050

# 5. Rodar API Flask
python src/api.py
# Acesse: http://127.0.0.1:5000

# 6. Rodar pipeline completo (passos 2, 3 e relatório)
python main.py
```

## 🗃️ Fontes de Dados

- [InfoDengue](https://info.dengue.mat.br) — casos semanais + clima integrados
- Código IBGE Recife: `2611606`
- [INMET](https://inmet.gov.br) — dados climáticos complementares (opcional)

## 👤 Autor

Desenvolvido como projeto de Big Data — Faculdade Estácio
João Vitor — joaovitorxd3343@hotmail.com
GitHub: https://github.com/JoaoVitorXdz/dengue-recife