from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title= 'Visão Restaurantes', layout='wide')

#----------------------------------------------
# Funções
#----------------------------------------------
def clean_code(df1):
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

def distancia(df1):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['Distance']= df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    distancia_media = np.round(df1['Distance'].mean(),2)
    return distancia_media

def avg_std_time_delivery(df1, festival, op):
    """
    Essa função calcula o tempo médio e o desvio padrão do tempo de entrega
    Parâmetros:
    Input:
        - df: dataframe com os dados necessarios para o calculo
        - op: tipo de operação
            'avg_time': calcula o tempo médio
            'std_time': calcula o desvio padrão do tempo
    Output:
        - df: dataframe com 2 colunas e 1 linha
    """
    cols = ['Time_taken(min)','Festival']
    df_aux = df1.loc[:,cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selecionadas, op],2)
    return df_aux

def avg_std_time_graph(df1):
    cols = ['Time_taken(min)','City']
    df_aux = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y= df_aux['avg_time'], error_y= dict(type='data', array= df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    cols = ['Time_taken(min)','City','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig= px.sunburst(df_aux, path=['City','Road_traffic_density'], values= 'avg_time',
                     color= 'std_time', color_continuous_scale='RdBu',
                     color_continuous_midpoint= np.average(df_aux['std_time']))
    return fig
#--------------------- Inicio da estrutura lógica do código -------------------------
# Leitura do arquivo CSV
df = pd.read_csv('train.csv')

df1=df.copy()
# Limpando os dados
df1= clean_code(df)

#----------------Streamlit-------------------
#----------------Barra Lateral----------------
st.header('Marketplace - Visão Restaurantes')

image= Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fasted Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qua valor?',
    value=pd.datetime(2022, 4, 13), 
    min_value=pd.datetime(2022, 2, 11), 
    max_value=pd.datetime(2022, 4, 6), 
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
        st.markdown("""---""")
        st.title('Métricas Gerais')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entregadores_unicos = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', entregadores_unicos)
        with col2:
            distancia_media= distancia(df1)
            col2.metric('Distância média das entregas',distancia_media)
           
            
        with col3:
            df_aux =  avg_std_time_delivery(df1,'Yes', 'avg_time')
            col3.metric('Tempo médio de entrega com Festival', df_aux)
            
        with col4:
            df_aux =  avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric('Desvio Padrão de entrega com Festival', df_aux)
        with col5:
            df_aux =  avg_std_time_delivery(df1,'No', 'avg_time')
            col5.metric('Tempo médio de entrega sem Festival', df_aux)
        with col6:
            df_aux =  avg_std_time_delivery(df1,'No', 'std_time')
            col6.metric('Desvio Padrão de entrega sem Festival', df_aux)
            
    with st.container():
        st.markdown("""---""")
        col1, col2= st.columns(2)
        with col1:
            st.markdown('### Tempo médio de entrega por cidade')
            fig= avg_std_time_graph(df1)
            st.plotly_chart(fig)
            
            
        with col2:
            st.markdown('### Distribuição da distância')
            cols = ['Time_taken(min)','City','Type_of_order']
            df_aux = df1.loc[:,cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
        
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Tempo médio de entrega por cidade')
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance']= df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            distancia_media = df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels= distancia_media['City'], values= distancia_media['Distance'], pull= [0, 0.1, 0])])
            st.plotly_chart(fig)
            
        with col2:
            st.markdown('### Distribuição do tempo')
            fig= avg_std_time_on_traffic(df1)          
            st.plotly_chart(fig)
          

       