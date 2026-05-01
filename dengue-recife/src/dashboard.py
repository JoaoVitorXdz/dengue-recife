import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.processing import carregar_e_processar

df = carregar_e_processar()
df['data'] = pd.to_datetime(df['data'])
anos = sorted([int(a) for a in df['ano'].unique()])

app = Dash(__name__)

app.layout = html.Div([
    html.H1("🦟 Dengue em Recife — Dashboard", style={'textAlign': 'center', 'fontFamily': 'Arial'}),

    html.Div([
        html.Label("Filtrar por ano:"),
        dcc.RangeSlider(
            id='slider-ano',
            min=anos[0], max=anos[-1], step=1,
            marks={a: str(a) for a in anos},
            value=[anos[0], anos[-1]]
        )
    ], style={'padding': '20px 40px'}),

    dcc.Graph(id='grafico-casos'),

    html.Div([
        dcc.Graph(id='grafico-temp', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='grafico-nivel', style={'width': '48%', 'display': 'inline-block'}),
    ])
], style={'fontFamily': 'Arial', 'maxWidth': '1200px', 'margin': 'auto'})


@app.callback(
    Output('grafico-casos', 'figure'),
    Output('grafico-temp',  'figure'),
    Output('grafico-nivel', 'figure'),
    Input('slider-ano', 'value')
)
def atualizar(anos_sel):
    filtro = df[(df['ano'] >= anos_sel[0]) & (df['ano'] <= anos_sel[1])]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=filtro['data'], y=filtro['casos_est'],
                              mode='lines', name='Casos estimados',
                              line=dict(color='crimson', width=2)))
    fig1.update_layout(title='Casos estimados de dengue por semana',
                       xaxis_title='Data', yaxis_title='Casos')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=filtro['data'], y=filtro['tempmed'],
                              mode='lines', name='Temp. média',
                              line=dict(color='orange')))
    fig2.update_layout(title='Temperatura média (°C)', xaxis_title='Data')

    nivel_counts = filtro['nivel'].value_counts().sort_index()
    cores = {1: 'green', 2: 'yellow', 3: 'orange', 4: 'red'}
    fig3 = go.Figure(go.Bar(
        x=[f'Nível {n}' for n in nivel_counts.index],
        y=nivel_counts.values,
        marker_color=[cores.get(n, 'gray') for n in nivel_counts.index]
    ))
    fig3.update_layout(title='Distribuição dos níveis de alerta')

    return fig1, fig2, fig3


if __name__ == '__main__':
    print("Dashboard rodando em: http://127.0.0.1:8050")
    app.run(debug=True)