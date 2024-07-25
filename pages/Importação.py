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
if "df_importacao" in st.session_state:
    df_imp = st.session_state["df_importacao"]

# Ajuste configuração de pagina
st.set_page_config(
    layout="wide",
    page_title="Importações",
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

ano_inicial = df_imp['CO_ANO'].min()
ano_final = df_imp['CO_ANO'].max()
####################################################################################################################
# Gráficos

# Agrupando os dados por País (TOP 20) / Valor Importado 
df_pais_imp = df_imp.groupby(['NO_PAIS'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(20)
df_pais_imp.sort_values(by='VL_FOB', ascending=False, inplace=True)
fig1 = px.bar(df_pais_imp, x='NO_PAIS', y = 'VL_FOB')


df_setor_ts_imp = df_imp.groupby(['ANO_MES','NO_ISIC_SECAO']).agg({'VL_FOB': 'sum'}).reset_index()
fig_ts_imp = px.line(df_setor_ts_imp, x='ANO_MES', y='VL_FOB', color='NO_ISIC_SECAO')

#####################################################################################################################
# KPI´s - Calculos adcionais (cards)

kgs_imp = df_imp['KG_LIQUIDO'].sum()
kgs_imp = f"{kgs_imp / 1e9:,.2f}"
imp_total = df_imp['VL_FOB'].sum()
imp_total = f"USD {imp_total / 1e9:,.2f}Bi"
qtde_paises_imp = df_imp['NO_PAIS'].nunique()

####################################################################################################################

header = st.container()

with header:
    st.image('icones/brasao.png', width=250)
    st.header(f'Visão geral das importações entre os anos de {ano_inicial} e {ano_final}!')

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric('**KGs Importados**', kgs_imp)

with col2:
    st.metric('**Total Exportações**', imp_total)

with col3:
    st.metric('**Qtde Paises (fornecedores)**', qtde_paises_imp)

st.divider()

col4, col5 = st.columns(2)

with col4:
    st.subheader(f'Total Importações entre os anos: {ano_inicial} a {ano_final}')
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader(f'Total Importações entre {ano_inicial} e {ano_final} por Setor Produtivo')
    st.plotly_chart(fig_ts_imp, use_container_width=True)
