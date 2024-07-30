import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

#-----------------------------------------------------------------------------------------------------------------#
## Configurações

# Ajuste configuração de pagina
st.set_page_config(
    layout="wide",
    page_title="COMEX - Balança Comercial",
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

# Utilizado para operações pesadas
@st.cache_data
def load_data(caminho):
    df = pd.read_parquet(caminho)
    return df

# Carregar e armazenar dados no session_state se ainda não estiverem lá
if "df_exportacao" not in st.session_state:
    st.session_state["df_exportacao"] = load_data('dados/df_exp.parquet')

if 'df_importacao' not in st.session_state:
    st.session_state['df_importacao'] = load_data('dados/df_imp.parquet')

# Acessar os dados do session_state
df_exp = st.session_state["df_exportacao"]
df_imp = st.session_state['df_importacao']

# Extrair o menor / maior Ano do dataset
ano_inicial = df_exp['CO_ANO'].min()
ano_final = df_exp['CO_ANO'].max()

# Ajustes nos dataframes
df_exp['CO_ANO'] = df_exp['CO_ANO'].astype(int)
df_imp['CO_ANO'] = df_imp['CO_ANO'].astype(int)

#-----------------------------------------------------------------------------------------------------------------#
# Criando dataframe com os dados da Balança Comercial 

# Dataframe_1
# Agrupando os dados por ANO_MES | EXP / IMP
df_ano_mes_exp = df_exp.groupby(['ANO_MES']).agg({'VL_FOB': 'sum'}).reset_index()
df_ano_mes_imp = df_imp.groupby(['ANO_MES']).agg({'VL_FOB': 'sum'}).reset_index()

# Concatenado os dataframes df_ano_mes (EXP/IMP)
df_ano_mes_merged = df_ano_mes_exp.merge(df_ano_mes_imp,
                                         how='left',
                                         left_on=['ANO_MES'],
                                         right_on=['ANO_MES'],
                                         suffixes=('_EXP', '_IMP'))

# Criando novas colunas
df_ano_mes_merged['BALANÇA_COMERCIAL'] = df_ano_mes_merged['VL_FOB_EXP'] - df_ano_mes_merged['VL_FOB_IMP']
df_ano_mes_merged['BALANÇA_COMERCIAL_ACC'] = df_ano_mes_merged['BALANÇA_COMERCIAL'].cumsum()
df_ano_mes_merged['%_VAR_EXPxIMP'] = (df_ano_mes_merged['VL_FOB_EXP'] / df_ano_mes_merged['VL_FOB_IMP'])-1
df_ano_mes_merged['ANO'] = df_ano_mes_merged['ANO_MES'].dt.year

# Dataframe_2
# Agrupando os dados por Grupo NCM | EXP / IMP
df_grupo_exp = df_exp.groupby(['NO_NCM_POR']).agg({'VL_FOB': 'sum'}).reset_index()
df_grupo_imp = df_imp.groupby(['NO_NCM_POR']).agg({'VL_FOB': 'sum'}).reset_index()

# Concatenado os dataframes df_grupo (EXP/IMP)
df_grupo_merged = df_grupo_exp.merge(df_grupo_imp,
                                         how='left',
                                         left_on=['NO_NCM_POR'],
                                         right_on=['NO_NCM_POR'],
                                         suffixes=('_EXP', '_IMP'))

#-----------------------------------------------------------------------------------------------------------------#
# Sidebar

# Adicionar a opção "Todos os Anos" à lista de anos
ano = ["Todos"] + df_ano_mes_merged['ANO'].unique().tolist()


#st.sidebar.header('Filtro 1')
ano_selecionado = st.sidebar.selectbox("Selecione o Ano", ano)

# Filtrar o DataFrame
if ano_selecionado == "Todos":
    df_ano_mes_merged_filtered = df_ano_mes_merged
else:
    df_ano_mes_merged_filtered = df_ano_mes_merged[df_ano_mes_merged['ANO'].isin([ano_selecionado])]

# Filtrar o DataFrame
if ano_selecionado == "Todos":
    df_exp_filtered = df_exp
else:
    df_exp_filtered = df_exp[df_exp['CO_ANO'].isin([ano_selecionado])]

#-----------------------------------------------------------------------------------------------------------------#
# Graficos

#df_ano_mes_merged_filtered = df_ano_mes_merged[df_ano_mes_merged['ANO'].isin([ano_selecionado])]

fig_var_bc = px.line(df_ano_mes_merged_filtered, x='ANO_MES', y="%_VAR_EXPxIMP")
fig_var_bc.update_xaxes(minor=dict(ticks="inside", showgrid=True))


fig_balanca_comercial = px.bar(df_ano_mes_merged_filtered, x='ANO_MES', y='BALANÇA_COMERCIAL')
fig_balanca_comercial.update_layout(yaxis=dict(title=None), xaxis=dict(title=None))

#-----------------------------------------------------------------------------------------------------------------#
# KPI´s - Calculos adcionais (cards)

perc_var_exp_imp = round(df_ano_mes_merged_filtered['%_VAR_EXPxIMP'].sum(),2)
perc_var_exp_imp = f"{perc_var_exp_imp:,.2f}%"
saldo_balanca = df_ano_mes_merged_filtered['BALANÇA_COMERCIAL'].sum()
saldo_balanca = f"USD {saldo_balanca / 1e9:,.2f}Bi"
exp_total = df_exp_filtered['VL_FOB'].sum()
exp_total = f"USD {exp_total / 1e9:,.2f}Bi"
qtde_paises_exp = df_exp_filtered['NO_PAIS'].nunique()
#-----------------------------------------------------------------------------------------------------------------#
# Tabelas

df_balanca_grupo = df_grupo_merged.groupby(['NO_NCM_POR']).agg({'VL_FOB_EXP': 'sum', 'VL_FOB_IMP': 'sum'}).reset_index()
df_balanca_grupo = df_balanca_grupo.sort_values(by='VL_FOB_EXP', ascending=False)

#-----------------------------------------------------------------------------------------------------------------#
# Main

header = st.container()
#dataframe = st.container() 

with header:
    st.image('icones/brasao.png', width=250)
    st.title('Bem vindo ao projeto COMEX - Balança Comercial')
    st.text('Aplicação web interativa, construída com Streamlit e Python, para visualização e análise da balança comercial brasileira.')

st.divider()

st.markdown(f'### Dados coletados entre os anos de **{ano_inicial}** a **{ano_final}**!')
st.empty()

col1, col2, col3, col4 = st.columns(4)

with col1:
    # st.text('% Var Exportação vs Importação')
    # st.subheader(f'{perc_var_exp_imp:,} %')
    st.metric('**% Var Exportação vs Importação**', perc_var_exp_imp)
with col2:
    # st.subheader('Saldo da Balança Comercial')
    # st.subheader(f'USD {saldo_balanca:,}')
    st.metric('**Saldo da Balança Comercial**', saldo_balanca)
with col3:
    # st.subheader('Total Exportações no periodo')
    # st.subheader(f'USD {exp_total:,}')
    st.metric('**Total Exportações**', exp_total)
with col4:
    # st.subheader('Qtde Paises (clientes)')
    # st.subheader(f'{qtde_paises_exp}')
    st.metric('**Qtde Paises (clientes)**', qtde_paises_exp)

st.divider()

col4, col5 = st.columns(2)
    
with col4:
    st.subheader('% Var Exp x Imp')
    st.plotly_chart(fig_var_bc, use_container_width=True)

with col5:
    st.subheader('Balança Comercial')
    st.plotly_chart(fig_balanca_comercial, use_container_width=True)

st.divider()

st.subheader('Tabela aberta por grupo vs Valor USD (EXP/IMP) - Periodo total')
st.dataframe(df_balanca_grupo, use_container_width=True, hide_index=True)

