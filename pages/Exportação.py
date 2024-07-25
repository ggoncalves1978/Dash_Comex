import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt

#-----------------------------------------------------------------------------------------------------------------#
## Configurações

# Verificando se o DataFrame está no session_state
if "df_exportacao" in st.session_state:
    df_exp = st.session_state["df_exportacao"]

# Ajuste configuração de pagina
st.set_page_config(
    layout="wide",
    page_title="Exportações",
    page_icon= ':bar_chart:')

st.markdown(
    """
    <style>
    .Balança_Comercial {
        background-color: #F5F5F5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#-----------------------------------------------------------------------------------------------------------------#
# Extrair o menor / maior Ano do dataset
ano_inicial = df_exp['CO_ANO'].min()
ano_final = df_exp['CO_ANO'].max()

# Ajustes nos dataframes
df_exp['CO_ANO'] = df_exp['CO_ANO'].astype(int)

#-----------------------------------------------------------------------------------------------------------------#
# Criação dataframe Setor Produtivo: Indústria de Transformação
df_ind_transf_exp = df_exp.query('NO_ISIC_SECAO == "Indústria de Transformação"')
df_ind_transf_exp_prod = df_ind_transf_exp.groupby(['NO_ISIC_SECAO','NO_CUCI_GRUPO'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(10)

# Dicionário criado para simplificar o nome dos produtos
produto_dict = {
    'Leite, creme de leite e laticínios, exceto manteiga ou queijo': 'Laticínios',
    'Açúcares e melaços': 'Açúcares e melaços',
    'Farelos de soja e outros alimentos para animais (excluídos cereais não moídos), farinhas de carnes e outros animais': 'Alimentos p/ Animais',
    'Óleos combustíveis de petróleo ou de minerais betuminosos (exceto óleos brutos)': 'Petróleo',
    'Carne bovina fresca, refrigerada ou congelada': 'Carne bovina'
}
# Lista criada para filtrar o dataframe 
produto_filtro = [
    'Leite, creme de leite e laticínios, exceto manteiga ou queijo',
    'Açúcares e melaços',
    'Farelos de soja e outros alimentos para animais (excluídos cereais não moídos), farinhas de carnes e outros animais',
    'Óleos combustíveis de petróleo ou de minerais betuminosos (exceto óleos brutos)',
    'Carne bovina fresca, refrigerada ou congelada'    
]

df_ind_transf_exp_prod_filtered = df_ind_transf_exp[df_ind_transf_exp['NO_CUCI_GRUPO'].isin(produto_filtro)]
df_ind_transf_exp_prod_filtered['PRODUTO'] = df_ind_transf_exp_prod_filtered['NO_CUCI_GRUPO'].apply(lambda x: produto_dict.get(x))

df_ind_transf_exp_ts_prod = df_ind_transf_exp_prod_filtered.groupby(['CO_ANO', 'PRODUTO'])['VL_FOB'].sum().reset_index()


# Criação dataframe Setor Produtivo: Agropecuária
df_agro_exp = df_exp.query('NO_ISIC_SECAO == "Agropecuária"')
df_agro_exp_cultivo = df_agro_exp.groupby(['NO_ISIC_SECAO','NO_CUCI_GRUPO'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(10)

# Dicionário criado para simplificar o nome dos produtos
cultura_dict = {
    'Soja': 'Soja',
    'Milho não moído, exceto milho doce': 'Milho',
    'Café não torrado': 'Café',
    'Algodão em bruto': 'Algodão',
    'Frutas e nozes não oleaginosas, frescas ou secas': 'Frutas'
}
# Lista criada para filtrar o dataframe
cultura_filtro = ['Soja', 'Milho não moído, exceto milho doce', 'Café não torrado', 'Algodão em bruto', 
                  'Frutas e nozes não oleaginosas, frescas ou secas']

df_agro_exp_cultivo_filtered = df_agro_exp[df_agro_exp['NO_CUCI_GRUPO'].isin(cultura_filtro)]
df_agro_exp_cultivo_filtered['CULTURA'] = df_agro_exp_cultivo_filtered['NO_CUCI_GRUPO'].apply(lambda x: cultura_dict.get(x))

df_agro_exp_ts_cultivo = df_agro_exp_cultivo_filtered.groupby(['CO_ANO', 'CULTURA'])['VL_FOB'].sum().reset_index()

#-----------------------------------------------------------------------------------------------------------------#
# Sidebar

# Adicionar a opção "Todos os Anos" à lista de anos
ano = ["Todos"] + df_exp['CO_ANO'].unique().tolist()

ano_selecionado = st.sidebar.selectbox("Selecione o Ano", ano)

# Filtrar o DataFrame
if ano_selecionado == "Todos":
    df_exp_filtered = df_exp
else:
    df_exp_filtered = df_exp[df_exp['CO_ANO'].isin([ano_selecionado])]

#-----------------------------------------------------------------------------------------------------------------#
# Gráfico 

# Pais - VL_Exp
df_pais_exp = df_exp_filtered.groupby(['NO_PAIS'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(20)
df_pais_exp.sort_values(by='VL_FOB', ascending=False, inplace=True)
fig1 = px.bar(df_pais_exp, x='NO_PAIS', y = 'VL_FOB', title='Total Exportações por país')

# Por setor produtivo - VL_Exp
df_setor_ts_exp = df_exp_filtered.groupby(['ANO_MES','NO_ISIC_SECAO']).agg({'VL_FOB': 'sum'}).reset_index()
fig_ts_exp = px.line(df_setor_ts_exp, x='ANO_MES', y='VL_FOB', color='NO_ISIC_SECAO', title='Total Exportações por Setor Produtivo')

# TOP 5 - Ind Transformação
fig_ts_exp_ind_transf_prod = px.line(df_ind_transf_exp_ts_prod, x='CO_ANO', y='VL_FOB', color='PRODUTO',
                                     title= 'Industria de Transformação | TOP 5 Produtos')

# TOP 5 - Agro
fig_ts_exp_agro_cultivo = px.line(df_agro_exp_ts_cultivo, x='CO_ANO', y='VL_FOB', color='CULTURA',
                                  title= 'Agricultura | TOP 5 Cultura')

#-----------------------------------------------------------------------------------------------------------------#
# KPI´s - Calculos adcionais (cards)

kgs_exp = df_exp_filtered['KG_LIQUIDO'].sum()
kgs_exp = f"{kgs_exp / 1e9:,.2f}"
exp_total = df_exp_filtered['VL_FOB'].sum()
exp_total = f"USD {exp_total / 1e9:,.2f}Bi"
qtde_paises_exp = df_exp_filtered['NO_PAIS'].nunique()

#-----------------------------------------------------------------------------------------------------------------#

header = st.container()

with header:
    st.image('icones/brasao.png', width=250)
    st.header(f'Visão geral das exportações entre os anos de {ano_inicial} e {ano_final}!')

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric('**KGs Exportados**', kgs_exp)
with col2:
    st.metric('**Total Exportações**', exp_total)
with col3:
    st.metric('**Qtde Paises (clientes)**', qtde_paises_exp)

st.divider()

col4, col5 = st.columns(2)

with col4:
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.plotly_chart(fig_ts_exp, use_container_width=True)

st.divider()
st.subheader('Abaixo segue a visão dos dois principais setores da balança comercial')
st.text(f'Periodo: {ano_inicial} à {ano_final}')
st.write('\n' * 2)

col6, col7 = st.columns(2)

with col6:
    st.plotly_chart(fig_ts_exp_ind_transf_prod, use_container_width=True)

with col7:
    st.plotly_chart(fig_ts_exp_agro_cultivo, use_container_width=True)