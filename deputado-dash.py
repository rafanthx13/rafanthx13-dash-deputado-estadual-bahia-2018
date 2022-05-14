import plotly.express as px
from dash import dcc
import dash
import pandas as pd
import json
from dash import html
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template # aplicar tema ao grafiscos plotly
import dash_bootstrap_components as dbc

# Build App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
theme_graphs = 'solar'
load_figure_template([theme_graphs])
# DarkThemes: SOLAR; CYBORG
# Outros temas: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/

############### Functions ###############

# filter df_deputado_cidade with votes by candidate per city by candidate
def get_df_deputado_city(deputado_name):
    url_key = df_deputado_info[
        df_deputado_info['Nome na urna'] == deputado_name]['deputado_url'].iloc[0]
    return pd.merge(
            df_deputado_info.rename(columns={'votes': 'totalVotes'}),
            df_deputado_cidade[ df_deputado_cidade['deputado_url'] == url_key],
            how="inner", left_on='deputado_url', right_on='deputado_url'
        )

# filter df_deputado_info by name
def get_df_deputado_row(deputado_name):
    return df_deputado_info[
        df_deputado_info['Nome na urna'] == deputado_name
    ]

def cast_float_to_br_int(anumber):
    return "{:,.0f}".format(anumber).replace(
        ',','x').replace('.',',').replace('x','.')

# convert money to R$
def cast_float_to_money(anumber):
    if(not anumber):
        return 'R$ 0,00'
    return "R$ {:,.2f}".format(anumber).replace(
        ',','x').replace('.',',').replace('x','.')


############### READ DATASETS ###############

# Cidades e Votos
df_deputado_cidade = pd.read_csv('./datasets/deputado_votes_by_city.csv', sep=';')

# TSE + Gazeta + Estadao
df_deputado_info =  pd.merge(
    pd.read_csv('./datasets/deputado_estadual_tse.csv', sep=';'),
    pd.read_csv('./datasets/deputado_gazeta_info.csv', sep=';'),
    how="inner", left_on='nrCandidato', right_on='Número'
)

df_deputado_info =  pd.merge( df_deputado_info,
    pd.read_csv('./datasets/deputado_bens_estadao.csv', sep=';').drop_duplicates('nr_candidato'),
    how="inner", left_on='Número', right_on='nr_candidato'
)

# GEOJSON
with open('./datasets/geojson-bahia-cities.json', encoding="utf-8") as response:
    municipios = json.load(response)
    
## Pre-Processing

# calculate ranks
df_deputado_info['rank_votes'] = df_deputado_info[
    'votes'].rank(method='first', ascending=False).apply(int)

df_deputado_info['BensDeclarados'] = df_deputado_info[
    'BensDeclarados'].fillna(-1.0)
df_deputado_info['rank_bens'] = df_deputado_info[
    'BensDeclarados'].rank(method='first', ascending=False).apply(int)

df_deputado_info['totalRecebido'] = df_deputado_info[
    'totalRecebido'].fillna(-1.0)
df_deputado_info['rank_campanha'] = df_deputado_info[
    'totalRecebido'].rank(method='first', ascending=False).apply(int)

# deletar com situacao indeferida
df_deputado_info = df_deputado_info.drop( df_deputado_info[
    df_deputado_info['Situação da candidatura'] == 'Indeferido'].index)
    
# Start Temp DF
## Necessario para ser o primeiro dado a ser carregado
first_deputado = 'Joao Isidorio'
df_temp_city = get_df_deputado_city(first_deputado)
df_temp_city['porcentagem'] = df_temp_city['percentage'].apply(
    lambda x: float(x.replace(',','.').replace('%','')))


############### GRAPH PLOTLY FUNCTION ###############

def plotly_map_plot(adf, coly, pretitle, hover_data=[]):
    fig = px.choropleth_mapbox(
        data_frame=adf.sort_values(coly, ascending=False).head(10),
        geojson=municipios, 
        color=coly, # valor a ser pintado # votes
        locations="cidade",  # nome do local
        featureidkey="properties.name", # nome da cidade no GeoJSON
        center = {"lat": -14.0902, "lon": -40.7129},
        mapbox_style="carto-positron",
        color_continuous_scale="inferno",
        hover_data=hover_data,
        template=theme_graphs,
        zoom=4)
    fig.update_layout(
        title_text = pretitle + ' - ' + adf.iloc[0]['Nome na urna'],
    )
    return fig


def plotly_bar_plot(adf, colx, coly, col_text, hover_data=[], rank=10, orderby=False):
    return px.bar(
        adf.sort_values(coly, ascending=orderby).head(rank),
        x=colx,
        y=coly,
        color=coly,
        color_continuous_scale="inferno",
        hover_data=hover_data,
        template=theme_graphs,
        text_auto=col_text
    )


############### GRAPH PLOTLY CREATE FIRST ###############

first_map_plot = plotly_map_plot(
    df_temp_city, coly='votes', pretitle='Qtd Votos',
    hover_data=['percentage'] 
)

first_bar_plot = plotly_bar_plot(
    df_temp_city, colx='cidade', coly='votes',
    col_text='votes', hover_data=['percentage'] 
)

fig_map_percentage = plotly_map_plot(
    df_temp_city, coly='porcentagem', pretitle='Porcentagem de Votos',
    hover_data=['percentage', 'totalVotes'] 
)

fig_bar_percentage = plotly_bar_plot(
    df_temp_city, colx='cidade', coly='porcentagem',
    col_text='percentage', hover_data=['votes'] 
)


############### STRUCTURE ###############

col1 = [
    html.H5("Escolha o Deputado Estadual:",
            style={"marginTop": "20px", 'marginBottom': '20px'}),
    html.Div(
        className="div-for-dropdown",
        id="div-test",
        style={'marginBottom': '20px'},
        children=[dcc.Dropdown(
            df_deputado_info['Nome na urna'],
            value=first_deputado, # coloca value para ja começar com algum selecionado
            id='deputado-dropdown'),
        ],
    ),
    dbc.Card([
            dbc.CardBody([
            html.B('Nome Completo: '),
                                html.Br(),
            html.Span(id='nomeCompleto'),
                html.Br(),
            html.B('Partido: '),
                                html.Br(),
            html.Span(id='nrPartido'),
            html.Span(' - '),
            html.Span(id='Partido'),
                html.Br(),
            html.B('N° Candidato: '),
            html.Span(id='nrCandidato')
        ])
    ], style={'padding': 0}),
    dbc.Card(dbc.CardBody([
            html.Span('Situação: '),
            html.B(id='eleito'),
        ])),
]

col2 = dbc.Card([
    dbc.CardImg(
        id='img',
        src="https://cdn-eleicoes.gazetadopovo.com.br/fotos/bahia/deputado-estadual/joao-isidorio-70000.jpg",
        style={'paddingTop': 15, 'width': '80%'}
    ),
], style={'textAlign': 'center'}, body=True)

col3 = [ dbc.Card(dbc.CardBody([
            html.B('Idade: '),
            html.Span(id='Idade'),
                html.Br(),
            html.B('Ocupação: '),
            html.Span(id='Ocupação'),
                html.Br(),
            html.B('Cor/Raça: '),
            html.Span(id='Cor/Raça'),
                    html.Br(),
            html.B('Estado Civil: '),
            html.Span(id='Estado Civil'),
                    html.Br(),
            html.B('Cidade nascimento: '),
            html.Span(id='Município de nascimento'),
                    html.Br(),
            html.B('Escolaridade: '),
            html.Span(id='Grau de instrução'),    
        ])),
        dbc.Card(dbc.CardBody([
            html.B('Gasto em Campanha: '),
                html.Br(),
            html.Span(id='totalRecebido'),
            html.Span(' \ rank: '),
            html.Span(id='rank_campanha'),
                html.Br(),
            html.B('Qtd Votos: '),
            html.Span(id='votes'),
            html.Span(' \ rank: '),
            html.Span(id='rank_votes'),
                html.Br(),
            html.B('Bens Declarados: '),
                html.Br(),
            html.Span(id='BensDeclarados'),
            html.Span(' \ rank: '),
            html.Span(id='rank_bens'),
        ])),
]

app.layout = dbc.Container(
    children=[
        # Titulo e Info Input
        dbc.Row([
            html.H1(children="DashBoard Eleições 2028 - Deputados Estaduais na Bahia"),
        ]),
        dbc.Row([
            dbc.Col(col1),
            
            dbc.Col(col2),
                
            dbc.Col(col3),
                
        ]),
        dbc.Row([
            html.H3(children="Cidades com maior quantidade de votos")
        ]),
        # Figuras
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=[
                            dcc.Graph(id="map-votes-number", figure=first_map_plot)
                        ],
                    ),
                ] )),
            ]),
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    dcc.Loading(
                        id="loading-2",
                        type="default",
                        children=[
                            dcc.Graph(id="bar-votes-number", figure=first_bar_plot)
                        ],
                    ),
                ])),
            ]),
        ]),
        #########
        dbc.Row([
            html.H3(children="Cidades com maior porcentagem de votos")
        ]),
        # Figuras
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    dcc.Loading(
                        id="loading-percentage-1",
                        type="default",
                        children=[
                            dcc.Graph(id="map-percentage", figure=fig_map_percentage)
                        ],
                    ),
                ] )),
            ]),
            dbc.Col([
                dbc.Card(dbc.CardBody([
                    dcc.Loading(
                        id="loading-percentage-2",
                        type="default",
                        children=[
                            dcc.Graph(id="bar-percentage", figure=fig_bar_percentage)
                        ],
                    ),
                ])),
            ]),
        ], style={'marginBottom': '30px'}),
        ####
        dbc.Row([
            html.Div([
                html.Span('Desenvolvido por Rafael Morais de Assis - '),
                html.A('GitHub Link', href='https://github.com/rafanthx13'),
                html.Span(' - Fonte dos dados: TSE, Gazeta do Povo, Estadão'),
            ]),
        ]),
], fluid=True)

############### CALL BACK & INTERATIVITY ###############

def get_deputado_info(deputado_name):
    r = df_deputado_info[ df_deputado_info['Nome na urna'] == deputado_name]
    list_attrs_output = ['nomeCompleto', 'img', 'Partido',
        'nrCandidato', 'nrPartido', 'Idade', 'Ocupação', 'Cor/Raça', 'Estado Civil',
        # part2
        'Município de nascimento', 'Grau de instrução', 'eleito',
        'BensDeclarados',
        # part3
        'rank_votes', 'rank_bens', 'rank_campanha',
]
    rest_list = []
    # total Recebido
    rest_list.append(cast_float_to_money(r['totalRecebido'].iloc[0]))
    rest_list.append(cast_float_to_br_int(r['votes'].iloc[0]))
    return tuple([r[el].iloc[0] for el in list_attrs_output] + rest_list)

@app.callback([
    Output('nomeCompleto', 'children'),
    Output('img', 'src'),
    Output('Partido', 'children'),
    Output('nrCandidato', 'children'),
    Output('nrPartido', 'children'),
    Output('Idade', 'children'),
    Output('Ocupação', 'children'),
    Output('Cor/Raça', 'children'),
    Output('Estado Civil', 'children'),
    # part 2
    Output('Município de nascimento', 'children'),
    Output('Grau de instrução', 'children'),
    Output('eleito', 'children'),
    Output('BensDeclarados', 'children'),
    # part3
    Output('rank_votes', 'children'),
    Output('rank_bens', 'children'),
    Output('rank_campanha', 'children'),
    # later data
    Output('totalRecebido', 'children'),
    Output('votes', 'children')],
    # Input
    Input('deputado-dropdown', 'value') )
def chose_deputado(deputado_name):
    global df_temp_city
    df_temp_city = get_df_deputado_city(deputado_name)
    df_temp_city['porcentagem'] = df_temp_city['percentage'].apply(lambda x: float(x.replace(',','.').replace('%','')))
    return get_deputado_info(deputado_name)


@app.callback(
    Output('map-votes-number', 'figure'),
    Output('bar-votes-number', 'figure'),
    Input('nomeCompleto', 'children') )
def update_map_votes_number(nome_deputado):
    global df_temp_city
    figre = plotly_map_plot(
        df_temp_city, coly='votes', pretitle='Qtd Votos',
        hover_data=['percentage','totalVotes'] 
    )
    fig2re = plotly_bar_plot(
        df_temp_city, colx='cidade', coly='votes', col_text='votes',
        hover_data=['votes', 'percentage', 'totalVotes', 'eleito'] 
    )
    return figre, fig2re

@app.callback(
    Output('map-percentage', 'figure'),
    Output('bar-percentage', 'figure'),
    Input('nomeCompleto', 'children'))
def update_map_votes_percentage(nome_deputado):
    global df_temp_city
    figre4 = plotly_map_plot(
        df_temp_city, coly='porcentagem', pretitle='Porcentagem Votos',
        hover_data=['percentage','votes'] 
    )
    fig_bar = plotly_bar_plot(
        df_temp_city, 'cidade', 'porcentagem',
        'percentage', hover_data=['votes', 'percentage']
    )
    return figre4, fig_bar

# END
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)