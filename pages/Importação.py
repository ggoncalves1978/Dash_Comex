import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
#-----------------------------------------------------------------------------------------------------------------#
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

#-----------------------------------------------------------------------------------------------------------------#
# Extrair o menor / maior Ano do dataset

ano_inicial = df_imp['CO_ANO'].min()
ano_final = df_imp['CO_ANO'].max()

# Ajustes nos dataframes
df_imp['CO_ANO'] = df_imp['CO_ANO'].astype(int)

#-----------------------------------------------------------------------------------------------------------------#
# Sidebar

# Adicionar a opção "Todos os Anos" à lista de anos
ano = ["Todos"] + df_imp['CO_ANO'].unique().tolist()

ano_selecionado = st.sidebar.selectbox("Selecione o Ano", ano)

# Filtrar o DataFrame
if ano_selecionado == "Todos":
    df_imp_filtered = df_imp
else:
    df_imp_filtered = df_imp[df_imp['CO_ANO'].isin([ano_selecionado])]

#-----------------------------------------------------------------------------------------------------------------#
# Gráficos

# Agrupando os dados por País (TOP 20) / Valor Importado 
df_pais_imp = df_imp_filtered.groupby(['NO_PAIS'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(20)
df_pais_imp.sort_values(by='VL_FOB', ascending=False, inplace=True)
fig1 = px.bar(df_pais_imp, x='NO_PAIS', y = 'VL_FOB', title='Total Importações por país')


df_setor_ts_imp = df_imp_filtered.groupby(['ANO_MES','NO_ISIC_SECAO']).agg({'VL_FOB': 'sum'}).reset_index()
fig_ts_imp = px.line(df_setor_ts_imp, x='ANO_MES', y='VL_FOB', color='NO_ISIC_SECAO', title='Total Importações por Setor Produtivo')

df_uf_imp = df_imp_filtered.groupby(['SG_UF_NCM'])['VL_FOB'].sum().sort_values(ascending=False).reset_index()
fig_2_uf = px.bar(df_uf_imp, x='SG_UF_NCM', y='VL_FOB', title='Total de importações por UF') 

#-----------------------------------------------------------------------------------------------------------------#
# KPI´s - Calculos adcionais (cards)

kgs_imp = df_imp_filtered['KG_LIQUIDO'].sum()
kgs_imp = f"{kgs_imp / 1e9:,.2f}"
imp_total = df_imp_filtered['VL_FOB'].sum()
imp_total = f"USD {imp_total / 1e9:,.2f}Bi"
qtde_paises_imp = df_imp_filtered['NO_PAIS'].nunique()

#-----------------------------------------------------------------------------------------------------------------#

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
    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.plotly_chart(fig_ts_imp, use_container_width=True)

st.divider()

st.plotly_chart(fig_2_uf, use_container_width=True)

# Criando dataframe por produto importado (TOP 10)
df_grupo_imp = df_imp_filtered.groupby(['NO_CUCI_GRUPO'])['VL_FOB'].sum().sort_values(ascending=False).reset_index().head(10)

st.markdown('**TOP 10 grupo de produtos**')
st.dataframe(df_grupo_imp, use_container_width=True, hide_index=True,)