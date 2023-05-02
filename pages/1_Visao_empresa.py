from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title= 'Visão Empresa', layout='wide')
#----------------------------------------------
# Funções
#----------------------------------------------
def country_maps(df1):
        """ 
            Essa função plota um gráfico com a localização central de cada cidade por tipo de tráfego.
        """
        cols= ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        df_aux = df.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()
        map = folium.Map()
        for index, location_info in df_aux.iterrows():
            folium.Marker(  [location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup= location_info[['City','Road_traffic_density']]).add_to(map)
        folium_static(map, width=1024, height=600)
                                      

def order_share_by_week(df1):
        """ 
            Essa função plota um gráfico com a quantidade de pedidos por entregador por semana.
        """
        cols= ['ID','Week_of_year']
        df_aux1 = df1.loc[:,cols].groupby('Week_of_year').count().reset_index()
        #Quantidade de entregadores unicos por semana
        cols= ['Delivery_person_ID','Week_of_year']
        df_aux2 = df1.loc[:,cols].groupby('Week_of_year').nunique().reset_index()
        #Juntar
        df_aux = pd.merge(df_aux1, df_aux2, how='inner')
        df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig= px.line(df_aux, x='Week_of_year', y='Order_by_deliver')
        return fig
    
def order_by_week(df1):
        """
            Essa função plota um gráfico com a Quantidade de pedidos por semana.
        """
        df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        cols= ['ID','Week_of_year']
        df_aux = df1.loc[:,cols].groupby('Week_of_year').count().reset_index()
        fig= px.line(df_aux, x='Week_of_year', y='ID')
        return fig
    
def traffic_order_city(df1):
        """
            Essa função plota um gráfico fazendo a Comparação do volume de pedidos por cidade e tipo de tráfego.
        """
        cols = ['ID','City','Road_traffic_density']
        df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index()
        fig= px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
        return fig  
    
def traffic_order_share(df1):
        """
            Essa função plota um gráfico com a Distribuição dos pedidos por tipo de tráfego.
        """
        cols=['ID','Road_traffic_density']
        df_aux = df1.loc[:,cols].groupby('Road_traffic_density').count().reset_index()
        #Calcular a porcentagem, criando a coluna entregas_perc
        df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
        fig= px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
        return fig

def order_metric(df1):
        """
            Essa função plota um gráfico com a Quantidade de pedidos por dia.
        """
        cols = ['ID','Order_Date']
        df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()
        fig= px.bar(df_aux, x='Order_Date', y='ID')
        return fig

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

#--------------------- Inicio da estrutura lógica do código -------------------------

# Importar o dataset
df = pd.read_csv('train.csv')
df1=df.copy()

# Limpando os dados
df1= clean_code(df)

#----------------Streamlit-------------------
#----------------Barra Lateral----------------
st.header('Marketplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])
with tab1:
    with st.container():
        #1. Quantidade de pedidos por dia.
        fig= order_metric(df1)
        st.markdown('Pedidos por dia')
        st.plotly_chart(fig, use_container_widht=True)
             
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            # 3. Distribuição dos pedidos por tipo de tráfego.
            fig= traffic_order_share(df1)
            st.header('Pedidos por tipo de tráfego')
            st.plotly_chart(fig, use_container_widht=True)
                     
        with col2:
            #4. Comparação do volume de pedidos por cidade e tipo de tráfego.
            st.header('Volume de pedidos por cidade e tipo de tráfego')
            fig= traffic_order_city(df1)
            st.plotly_chart(fig, use_container_widht=True)
            
with tab2:
    with st.container():
        #2. Quantidade de pedidos por semana.
        st.markdown('Pedidos por semana')
        fig= order_by_week(df1)
        st.plotly_chart(fig, use_container_widht=True)
         
    with st.container():
        #4. A quantidade de pedidos por entregador por semana.
        st.markdown('Quantidade de pedidos por entregador por semana')
        fig= order_share_by_week(df1)
        st.plotly_chart(fig, use_container_widht=True)
       
        
with tab3:
    #5. A localização central de cada cidade por tipo de tráfego.
    st.markdown('Localização central de cada cidade por tipo de tráfego')
    country_maps(df1)
   