import streamlit as st
import pandas as pd
import os
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title='Painel AIPS', page_icon='map_chart', layout='wide')


def load_data():
    df = pd.read_csv('AISP.csv')
    df = df.dropna(subset=['latitude', 'longitude', 'Municípios', 'BPM/CIA', 'Georeferenciamento', 'RISP', 'AISP'])
    df['RISP'] = df['RISP'].str.strip().str.replace(' ', '')
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.dropna(subset=['latitude', 'longitude'])
    return df

df = load_data()

bpm_cia_options = df['BPM/CIA'].dropna().unique()
georeferenciamento_options = df['Georeferenciamento'].dropna().unique()
risp_options = df['RISP'].dropna().unique()
aisp_options = df['AISP'].dropna().unique()
municipios_options = df['Municípios'].dropna().unique()

def get_filtered_data(municipio, bpm_cia, risp, georeferenciamento, aisp):
    df_filtrado = df
    
    if municipio:
        df_filtrado = df_filtrado[df_filtrado['Municípios'].str.contains(municipio, case=False, na=False)]

    if bpm_cia:
        df_filtrado = df_filtrado[df_filtrado['BPM/CIA'].str.contains(bpm_cia, case=False, na=False)]

    if risp:
        df_filtrado = df_filtrado[df_filtrado['RISP'] == risp]

    if georeferenciamento:
        df_filtrado = df_filtrado[df_filtrado['Georeferenciamento'] == georeferenciamento]

    if aisp:
        df_filtrado = df_filtrado[df_filtrado['AISP'] == aisp]
    
    return df_filtrado

with st.sidebar:
    st.sidebar.header("PAINEL AISP")
    st.sidebar.image('logo_ssp.png', width=220)
    st.sidebar.subheader('Filtros')

with st.sidebar.expander("Municípios"):
    municipio = st.selectbox('', options=[''] + list(municipios_options))  # Adiciona uma opção vazia para "Todos"
    
        
with st.sidebar.expander("BPM/CIA"):
    bpm_cia = st.selectbox('', options=[''] + list(bpm_cia_options))  # Adiciona uma opção vazia para "Todos"
   

with st.sidebar.expander("RISP"):
    risp = st.selectbox('', options=[''] + list(risp_options))  # Adiciona uma opção vazia para "Todos"
    

with st.sidebar.expander("AISP"):
    georeferenciamento = st.selectbox('Georeferenciamento', options=[''] + list(georeferenciamento_options))  # Adiciona uma opção vazia para "Todos"
    aisp = st.selectbox('AISP', options=[''] + list(aisp_options))  # Adiciona uma opção vazia para "Todos"


filtered_df = get_filtered_data(municipio, bpm_cia, risp, georeferenciamento, aisp)

icon_paths = {
    'I': os.path.join(os.getcwd(), 'risp1.png'),
    'II': os.path.join(os.getcwd(), 'risp2.png'),
    'III': os.path.join(os.getcwd(), 'risp3.png'),
    'IV': os.path.join(os.getcwd(), 'risp4.png')
}

mapa = folium.Map(location=[filtered_df['latitude'].mean(), filtered_df['longitude'].mean()], zoom_start=7)

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <div style="width: 200px; padding: 5px;">
            <b>Município:</b> {row['Municípios']}<br>
            <b>BPM/CIA:</b> {row['BPM/CIA']}<br>
            <b>Endereço:</b> {row['Endereco']}<br>
            <b>Status:</b> {row['STATUS']}
        </div>
        """
        icon_path = icon_paths.get(row['RISP'], os.path.join(os.getcwd(), 'default_icon.png'))
        icon = folium.CustomIcon(icon_image=icon_path, icon_size=(15, 15))

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_html,
            tooltip=row['BPM/CIA'],
            icon=icon
        ).add_to(mapa)


with st.container(border=True):

    st.title('Rótulos')
    # Exibir as métricas
    col1, col2 = st.columns(2)

  
    with col1:
        risp_metric = st.metric("RISP", "-")
        municipios_metric = st.metric("Municípios", "-")
    with col2:
        bpm_cia_metric = st.metric("BPM/CIA", "-")
        aisp_metric = st.metric("AISP", "-")

with st.container(border=True):

    st.title('Mapa das RISP')
    # Mostrar o mapa e capturar a interação
    map_data = st_folium(mapa, width=1400, height=600)

    # Atualizar métricas com base no ponto clicado
    if map_data.get("last_object_clicked"):
        clicked_lat = map_data["last_object_clicked"].get("lat")
        clicked_lon = map_data["last_object_clicked"].get("lng")

        clicked_point = filtered_df[(filtered_df['latitude'] == clicked_lat) & (filtered_df['longitude'] == clicked_lon)]
        if not clicked_point.empty:
            clicked_data = clicked_point.iloc[0]
            risp_metric.metric("RISP", clicked_data['RISP'])
            aisp_metric.metric("AISP", clicked_data['AISP'])
            municipios_metric.metric("Municípios", clicked_data['Municípios'])
            bpm_cia_metric.metric("BPM/CIA", clicked_data['BPM/CIA'])
            
st.write(filtered_df)
