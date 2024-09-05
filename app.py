import streamlit as st
import folium
from streamlit.components.v1 import html
import pandas as pd
import os

st.set_page_config(page_title='Painel AIPS', page_icon='map_chart', layout='wide')

# Carregar o arquivo CSV
df = pd.read_csv('AISP.csv')

# Remover linhas com NaN nas colunas críticas
df = df.dropna(subset=['latitude', 'longitude', 'Municípios', 'BPM/CIA', 'Georeferenciamento', 'RISP', 'AISP'])

# Tratamento da coluna 'RISP' para remover espaços extras
df['RISP'] = df['RISP'].str.strip()  # Remove espaços no início e no fim
df['RISP'] = df['RISP'].str.replace(' ', '')  # Remove espaços internos

# Converter as colunas de latitude e longitude para float
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Remover valores NaN depois de converter
df = df.dropna(subset=['latitude', 'longitude'])

# Obter as opções únicas para cada filtro
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

# Sidebar com filtros dentro de expanders
with st.sidebar:
    
    st.sidebar.header("PAINEL AISP")
    st.sidebar.image('logo_ssp.png', width=220)
    st.sidebar.subheader('Filtros')

with st.sidebar.expander("Municípios"):
    municipio = st.selectbox('', options=[''] + list(municipios_options))  # Adiciona uma opção vazia para "Todos"
    if st.button('Limpar Município'):
        municipio = ''
        

with st.sidebar.expander("BPM/CIA"):
    bpm_cia = st.selectbox('', options=[''] + list(bpm_cia_options))  # Adiciona uma opção vazia para "Todos"
    if st.button('Limpar BPM/CIA'):
        bpm_cia = ''

with st.sidebar.expander("RISP"):
    risp = st.selectbox('', options=[''] + list(risp_options))  # Adiciona uma opção vazia para "Todos"
    if st.button('Limpar RISP'):
        risp = ''

with st.sidebar.expander("AISP"):
    georeferenciamento = st.selectbox('Georeferenciamento', options=[''] + list(georeferenciamento_options))  # Adiciona uma opção vazia para "Todos"
    if st.button('Limpar Georeferenciamento'):
        georeferenciamento = ''


    aisp = st.selectbox('AISP', options=[''] + list(aisp_options))  # Adiciona uma opção vazia para "Todos"
    if st.button('Limpar AISP'):
        aisp = ''

# Aplicar os filtros ao DataFrame
filtered_df = get_filtered_data(municipio, bpm_cia, risp, georeferenciamento, aisp)



# Caminho para as imagens dos ícones personalizados
icon_paths = {
    'I': os.path.join(os.getcwd(), 'risp1.png'),  # Ícone para RISP I
    'II': os.path.join(os.getcwd(), 'risp2.png'),  # Ícone para RISP II
    'III': os.path.join(os.getcwd(), 'risp3.png'),  # Ícone para RISP III
    'IV': os.path.join(os.getcwd(), 'risp4.png')   # Ícone para RISP IV
}

# Criar o mapa
if not filtered_df.empty:
    mapa = folium.Map(location=[filtered_df['latitude'].mean(), filtered_df['longitude'].mean()], zoom_start=7)

    # Adicionar os pontos ao mapa com Tooltip e Popup, usando ícones personalizados
    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <div style="width: 200px; padding: 5px;">
            <b>Município:</b> {row['Municípios']}<br>
            <b>BPM/CIA:</b> {row['BPM/CIA']}<br>
            <b>Endereço:</b> {row['Endereco']}<br>
            <b>Status:</b> {row['STATUS']}
        </div>
        """
        # Escolher o ícone com base no valor de 'RISP'
        icon_path = icon_paths.get(row['RISP'], os.path.join(os.getcwd(), 'default_icon.png'))  # Ícone padrão caso 'RISP' não esteja no dicionário
        icon = folium.CustomIcon(icon_image=icon_path, icon_size=(30, 30))  # Define o tamanho do ícone

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),  # Define a largura máxima do popup
            tooltip=row['BPM/CIA'],
            icon=icon  # Usa o ícone personalizado
        ).add_to(mapa)

    # Converter o mapa para HTML e exibi-lo no Streamlit
    st.title('Mapa')
    map_html = mapa._repr_html_()
    html(map_html, height=700, width=1100)
    # Verificar as primeiras linhas do DataFrame filtrado
    st.write(filtered_df)
else:
    st.write("Nenhum dado encontrado com os filtros aplicados.")
