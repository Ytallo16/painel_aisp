import streamlit as st
import folium
from streamlit.components.v1 import html
import pandas as pd

st.set_page_config(page_title='Painel AIPS', page_icon='map_chart', layout='wide')

# Carregar o arquivo CSV
df = pd.read_csv('AISP.csv')

# Tratamento da coluna 'RISP' para remover espaços extras
df['RISP'] = df['RISP'].str.strip()  # Remove espaços no início e no fim
df['RISP'] = df['RISP'].str.replace(' ', '')  # Remove espaços internos

# Filtrar registros com valor em 'RISP'
df = df.dropna(subset=['latitude', 'longitude', 'RISP'])
df = df[df['RISP'] != '']

# Verificar as primeiras linhas para entender o conteúdo
st.write(df)

# Converter as colunas de latitude e longitude para float
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Remover valores NaN depois de converter
df = df.dropna(subset=['latitude', 'longitude'])

# Criar um dicionário de cores para cada RISP
risp_colors = {
    'I': 'yellow',
    'II': 'purple',
    'III': 'orange',
    'IV': 'red'
}

# Criar o mapa
mapa = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=7)

# Adicionar os pontos ao mapa com Tooltip e Popup, e cor baseada em RISP
for _, row in df.iterrows():
    risp_color = risp_colors.get(row['RISP'], 'gray')  # Cor padrão se RISP não estiver no dicionário
    popup_html = f"""
    <div style="width: 200px; padding: 5px;">
        <b>Município:</b> {row['Municípios']}<br>
        <b>BPM/CIA:</b> {row['BPM/CIA']}<br>
        <b>Endereço:</b> {row['Endereco']}<br>
        <b>Status:</b> {row['STATUS']}
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_html, max_width=300),  # Define a largura máxima do popup
        tooltip=row['BPM/CIA'],
        icon=folium.Icon(icon='info-sign', color=risp_color)  # Define a cor do ícone
    ).add_to(mapa)

# Converter o mapa para HTML e exibi-lo no Streamlit
map_html = mapa._repr_html_()
html(map_html, height=800, width=1400)
