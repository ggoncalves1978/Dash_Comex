import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt

################################################################################################################
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

####################################################################################################################
# Extrair o menor / maior Ano do dataset

ano_inicial = df_exp['CO_ANO'].min()
ano_final = df_exp['CO_ANO'].max()
####################################################################################################################
# Gráfico 

# Pais Exp
df_pais_exp = df_exp.groupby(['NO_PAIS'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(20)
df_pais_exp.sort_values(by='VL_FOB', ascending=False, inplace=True)
fig1 = px.bar(df_pais_exp, x='NO_PAIS', y = 'VL_FOB')


df_setor_ts_exp = df_exp.groupby(['ANO_MES','NO_ISIC_SECAO']).agg({'VL_FOB': 'sum'}).reset_index()
fig_ts_exp = px.line(df_setor_ts_exp, x='ANO_MES', y='VL_FOB', color='NO_ISIC_SECAO')

####################################################################################################################
# KPI´s - Calculos adcionais (cards)

kgs_exp = df_exp['KG_LIQUIDO'].sum()
kgs_exp = f"{kgs_exp / 1e9:,.2f}"
exp_total = df_exp['VL_FOB'].sum()
exp_total = f"USD {exp_total / 1e9:,.2f}Bi"
qtde_paises_exp = df_exp['NO_PAIS'].nunique()

####################################################################################################################

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
    st.subheader(f'Total Exportações entre os anos: {ano_inicial} a {ano_final}')
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader(f'Total Exportações entre {ano_inicial} e {ano_final} por Setor Produtivo')
    st.plotly_chart(fig_ts_exp, use_container_width=True)

