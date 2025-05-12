## Imports e Configuração do Estilo

```python
#Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display

#Configuração do estilo 
plt.style.use('ggplot')
sns.set_palette("pastel")
pd.set_option('display.max_columns', None)
```

<br>
<hr>

## Carregando o Dataset e Informações Iniciais

```python
#Carregando os dados do dataset .CSV
df = pd.read_csv('dados/Sales.csv')


#Visualizando as primeiras linhas
print(df.head())

#Informações sobre o dataset
print("\nInformações do dataset:")
print(df.info())


#Estatísticas descritivas
print("\nEstatísticas descritivas:")
print(df.describe(include='all'))
```

<br>
<hr>

## Limpeza e Tratamento dos Dados

```python
#Verificando se há valores nulos
print("\nValores nulos por coluna:")
print(df.isnull().sum())

#Convertendo a coluna Date para o tipo correto dela (datetime)
df['Date'] = pd.to_datetime(df['Date'])

#Extraindo o ano, mês e dia da semana da coluna de Date
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()
df['Day_of_week'] = df['Date'].dt.day_name()

#Verificando a consistência dos dados categóricos
print("\nValores únicos em colunas categóricas:")
print("Country:", df['Country'].unique())
print("Product_Category:", df['Product_Category'].unique())
print("Sub_Category:", df['Sub_Category'].unique())
print("Product:", df['Product'].unique())

#Criando a coluna: margem de lucro
df['Profit_Margin'] = (df['Profit'] / df['Revenue']) * 100

#Verificando os outliers em valores numéricos
numeric_cols = ['Customer_Age', 'Order_Quantity', 'Unit_Cost', 'Unit_Price', 'Profit', 'Cost', 'Revenue', 'Profit_Margin']
df[numeric_cols].describe()

df['Profit_Margin'].sum()
```

<br>
<hr>

# Análise Exploratória

### Análise Temporal

```python
#Preparando os dados para a análise exploratória
monthly_data = df.groupby(['Year', 'Month']).agg({'Revenue':'sum', 'Profit':'sum'}).reset_index()

#Ordenando os meses na ordem correta
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_data['Month'] = pd.Categorical(monthly_data['Month'], categories=month_order, ordered=True)
monthly_data = monthly_data.sort_values(['Year', 'Month'])

#Criando o gráfico de área
fig = px.area(monthly_data, 
              x='Month', 
              y=['Revenue', 'Profit'],
              color='Year',
              facet_col='Year',
              title='Evolução Mensal de Receita e Lucro por Ano',
              labels={'value': 'Valor ($)', 'variable': 'Métrica'},
              template='plotly_white')


#Melhorando a formatação do gráfico
fig.update_layout(
    hovermode='x unified',
    yaxis_title='Valor ($)',
    legend_title='Métrica/Ano',
    height=500
)

#Mostrando os valores no hover de forma mais clara
fig.update_traces(
    hovertemplate='<b>%{x}</b><br>Valor: $%{y:,.0f}'
)

fig.show()
```

<br>

### Análise por Demografia

```python
#Quantidade de Vendas por país e estado
sales_by_location = df.groupby(['Country', 'State']).agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_Quantity': 'sum'
}).reset_index().sort_values('Revenue', ascending=False)

#Criando o Gráfico de barras 
fig = px.bar(sales_by_location.head(20), x='State', y='Revenue',
             color='Country', title='Top 20 Estados por Receita',
             hover_data=['Profit', 'Order_Quantity'],
             template='plotly_white')
fig.update_layout(xaxis={'categoryorder':'total descending'})
fig.show()
```

<br>

### Análise de Produtos

```python
#Vendas por categoria dos produtos
sales_by_product = df.groupby(['Product_Category', 'Sub_Category', 'Product']).agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_Quantity': 'sum',
    'Profit_Margin': 'mean'
}).reset_index().sort_values('Revenue', ascending=False)

#Criando o Gráfico de treemap 
fig = px.treemap(sales_by_product, path=['Product_Category', 'Sub_Category', 'Product'], 
                 values='Revenue', color='Profit_Margin',
                 color_continuous_scale='RdYlGn',
                 title='Distribuição de Receita por Categoria de Produto',
                 hover_data=['Order_Quantity', 'Profit'])
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
fig.show()
```

<br>

### Análise de Clientes

```python
#Vendas por faixa etária  e gênero
sales_by_demo = df.groupby(['Age_Group', 'Customer_Gender']).agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Customer_Age': 'count'
}).rename(columns={'Customer_Age': 'Count'}).reset_index()

#Criando o Gráfico de barras agrupadas
fig = px.bar(sales_by_demo, x='Age_Group', y='Revenue',
             color='Customer_Gender', barmode='group',
             title='Receita por Faixa Etária e Gênero',
             hover_data=['Profit', 'Count'],
             template='plotly_white')
fig.update_layout(xaxis={'categoryorder':'total descending'})
fig.show()
```




