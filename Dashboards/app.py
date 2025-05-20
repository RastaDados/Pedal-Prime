#Imports
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from pyngrok import ngrok

#Carregando os dados do arquivo CSV
df = pd.read_csv('dados/Sales.csv')


#Realizando o pré-processamento dos dados
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
df['Profit_Margin'] = (df['Profit'] / df['Revenue']) * 100



#Inicializando o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Necessário para deploy


#Configurando o layout do dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard de Vendas Pedal Prime", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Selecione o País:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in df['Country'].unique()],
                value=df['Country'].unique()[0],
                clearable=False
            )
        ], width=4),
        
        dbc.Col([
            html.Label("Selecione o Ano:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in sorted(df['Year'].unique())],
                value=sorted(df['Year'].unique())[0],
                clearable=False
            )
        ], width=4),
        
        dbc.Col([
            html.Label("Selecione a Métrica:"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Receita', 'value': 'Revenue'},
                    {'label': 'Lucro', 'value': 'Profit'},
                    {'label': 'Quantidade Vendida', 'value': 'Order_Quantity'},
                    {'label': 'Margem de Lucro (%)', 'value': 'Profit_Margin'}
                ],
                value='Revenue',
                clearable=False
            )
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-chart'), width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='geo-chart'), width=6),
        dbc.Col(dcc.Graph(id='product-treemap'), width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='demographic-chart'), width=6),
        dbc.Col(dcc.Graph(id='scatter-plot'), width=6)
    ])
], fluid=True)


#Criando e configurando os callbacks para o usuário interagir no app
@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('geo-chart', 'figure'),
     Output('product-treemap', 'figure'),
     Output('demographic-chart', 'figure'),
     Output('scatter-plot', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_dashboard(selected_country, selected_year, selected_metric):
    
    #Filtrando os dados
    filtered_df = df[(df['Country'] == selected_country) & (df['Year'] == selected_year)]


    #Criando o Gráfico de série temporal
    time_series_data = filtered_df.groupby('Month').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Order_Quantity': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    time_series_fig = px.line(time_series_data, x='Month', y=selected_metric,
                             title=f'{selected_metric} por Mês em {selected_year} - {selected_country}')
    
    
    #Criando o Gráfico de análise geográfica
    geo_data = filtered_df.groupby('State').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Order_Quantity': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index().sort_values(selected_metric, ascending=False)
    
    geo_fig = px.bar(geo_data.head(10), x='State', y=selected_metric,
                    title=f'Top 10 Estados por {selected_metric}',
                    hover_data=['Revenue', 'Profit', 'Profit_Margin'])
    
    
    #Criando o gráfico de treemap de produtos
    product_data = filtered_df.groupby(['Product_Category', 'Sub_Category', 'Product']).agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Order_Quantity': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index().sort_values(selected_metric, ascending=False)
    
    product_fig = px.treemap(product_data, path=['Product_Category', 'Sub_Category', 'Product'], 
                           values=selected_metric, color='Profit_Margin',
                           title=f'Distribuição de {selected_metric} por Produto')
    
    
    #Criando o gráfico de análise demográfica
    demo_data = filtered_df.groupby(['Age_Group', 'Customer_Gender']).agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Order_Quantity': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    demo_fig = px.bar(demo_data, x='Age_Group', y=selected_metric,
                     color='Customer_Gender', barmode='group',
                     title=f'{selected_metric} por Grupo Etário e Gênero')
    
    
    #Criando o Gráfico de dispersão
    scatter_fig = px.scatter(filtered_df, x='Order_Quantity', y='Profit',
                           color='Product_Category',
                           title='Relação entre Quantidade Vendida e Lucro')
    
    
    #Aplicando um template com estilo branco
    for fig in [time_series_fig, geo_fig, product_fig, demo_fig, scatter_fig]:
        fig.update_layout(template='plotly_white')
    
    return time_series_fig, geo_fig, product_fig, demo_fig, scatter_fig

if __name__ == '__main__':
    app.run_server(debug=True) 