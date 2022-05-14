# Dicas para fazer o Dashboard com `Dash + Plotly`

## Construção de gráficos

Mesmo que seja interativo, ao abrir o DashBoard é bom já ter dados default para mostrar. Ser a primeira coisa a ser visa. Se nâo fica tudo vaziu ao abrir a página.

## Dicas

+ A construção dos gráficos é bom fazer com função com diversos parÂmetros, pois vaiz usar pelo menos duas vezes: uma para ser o 1 gráficos e outra para atualizações

+ É possível separar as partes do HTML em variáveis, o que facilita na hora de cosntruir o layout.

+ `chose_deputado` com `get_deputado_info`. Com essa duas funções conseigo selecionar valores de uma row ao filtarr um *dataframe*

+ Os atributos CSS são escritos como camelCase, já que o front-end é feito em react

+ Todos os componente `html` ou `dbc` tem como primeiro parâmetro `children`, que é o `get_text()` real daquele componete, ou um outro comonente html/dbc

## Preparar arquivo `py` para deploy no Heroku

É preciso ter as seguintes coisas:

Ínicio do arquivo. `Dash`

````python
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
# Esser `server` é o que é chamdo pelo Procfile com gunicorn no heroku
server = app.server
````

Fim do Arquivo

````python
# END
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
````
