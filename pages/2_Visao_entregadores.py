from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title= 'Visão Entregadores', layout='wide')
#----------------------------------------------
# Funções
#----------------------------------------------
def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipo de Limpeza:
        1-Remoção dos dados NaN
        2-Mudança do tipo da coluna de dados
        3-Remoção dos espaços das variaveis de texto
        4-Formatação da coluna de datas
        5-Remoção do texto da variavel numérica
        Input: Dataframe
        Output: Dataframe
    """
    #Removendo espaço após a string
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()

    # Excluir as linhas vazias
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = df1['Festival'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :].copy()

    #Conversão de tipo
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    #Limpando a coluna time taken min
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int) 
    print(df1.head())
    return df1

 
def top_entregadores(df1, top_asc):
    """
        Essa função retorna os top entregadores mais rápidos e mais lentos
        para escolher entre os mais rapidos e mais lentos usamos o top_asc recebendo o valor True ou False
    """
    cols= ['Delivery_person_ID','City','Time_taken(min)']
    df2 = (df1.loc[:, cols]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending=top_asc)
              .reset_index())
    df_aux01= df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02= df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03= df2.loc[df2['City'] == 'Semi-Urban',:].head(10)
    df3= pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3

#--------------------- Inicio da estrutura lógica do código -------------------------

# Importar o dataset
df = pd.read_csv('train.csv')
df1=df.copy()

# Limpando os dados
df1= clean_code(df)

#----------------Streamlit-------------------
#----------------Barra Lateral----------------
st.header('Marketplace - Visão Entregadores')

image= Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fasted Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qua valor?',
    value=pd.Timestamp(2022, 4, 13), 
    min_value=pd.Timestamp(2022, 2, 11), 
    max_value=pd.Timestamp(2022, 4, 6), 
    format='DD-MM-YYYY')
st.header(date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Victor Corvino')
#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]


# --------------- Layout--------------
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            #menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            cols=['Delivery_person_ID','Delivery_person_Ratings']
            avaliacao_media_entregador = round(df1.loc[:,cols].groupby('Delivery_person_ID').mean().reset_index(),2)
            st.dataframe(avaliacao_media_entregador)
        with col2:
            st.markdown('##### Avaliação por condição de tráfego')
            cols=['Road_traffic_density','Delivery_person_Ratings']
            avaliacao_transito = df1.loc[:,cols].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean','std']})
            #corrigir a formatação da tabela
            avaliacao_transito.columns= ['delivery_mean','delivery_std']
            avaliacao_transito= avaliacao_transito.reset_index()
            st.dataframe(avaliacao_transito)
            
            st.markdown('##### Avaliação por condição climática')
            cols= ['Delivery_person_Ratings','Weatherconditions']
            avaliacao_clima= df1.loc[:,cols].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']})
            avaliacao_clima.columns=['delivery_mean','delivery_std']
            avaliacao_clima= avaliacao_clima.reset_index()
            st.dataframe(avaliacao_clima)
           
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Entregadores mais rápidos')
            df3= top_entregadores(df1, top_asc= True)
            st.dataframe(df3)
        with col2:
            st.markdown('##### Entregadores mais lentos')
            df3= top_entregadores(df1, top_asc= False)
            st.dataframe(df3)
           
