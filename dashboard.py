import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Resultados Votación", layout="wide")

# --- DATOS DE ESTUDIANTES (Para traducir RUT a Nombre) ---
ESTUDIANTES = [
    {"rut": "236669998", "nombre": "JULIAN AGUILAR"},
    {"rut": "237771052", "nombre": "ELOISA AHUMADA"},
    {"rut": "235812002", "nombre": "FELIPE AMBIADO"},
    {"rut": "238080614", "nombre": "FELIPE ARRIAGADA"},
    {"rut": "237693469", "nombre": "AGUSTIN CAMUS"},
    {"rut": "236455750", "nombre": "TAREK CHAMAS"},
    {"rut": "237679520", "nombre": "PEDRO FREIRE"},
    {"rut": "236588041", "nombre": "ALONSO GALDAMES"},
    {"rut": "238560136", "nombre": "LEONOR GIACAMAN"},
    {"rut": "237505468", "nombre": "MAITE GILLET"},
    {"rut": "238188180", "nombre": "CONSUELO GUZMAN"},
    {"rut": "237165632", "nombre": "TEODORO HERNANDO"},
    {"rut": "236909026", "nombre": "SEBASTIAN IBAR"},
    {"rut": "237720474", "nombre": "AGUSTIN JELVES"},
    {"rut": "236203751", "nombre": "SOFIA LAGOS"},
    {"rut": "237052331", "nombre": "MAITE MEJIAS"},
    {"rut": "235501716", "nombre": "AGUSTÍN MONTENEGRO"},
    {"rut": "237462653", "nombre": "CATALINA ODINO"},
    {"rut": "236234088", "nombre": "EMILIA OLMOS"},
    {"rut": "236646793", "nombre": "DAMIAN PETERMANN"},
    {"rut": "235293692", "nombre": "VITTORIO PIAGGIO"},
    {"rut": "238139104", "nombre": "ANTONIO PINO"},
    {"rut": "238891191", "nombre": "MAURICIO PIZARRO"},
    {"rut": "234124293", "nombre": "HELENA SANHUEZA"},
    {"rut": "23567744K", "nombre": "ALICIA VARGAS"},
    {"rut": "236857417", "nombre": "VALENTIN VILLARROEL"}
]

# Crear diccionario para búsqueda rápida RUT -> Nombre
rut_a_nombre = {e['rut']: e['nombre'] for e in ESTUDIANTES}

# --- FUNCIÓN DE CARGA ---
def cargar_datos(uploaded_file=None):
    # Si el usuario sube un archivo, usar ese
    if uploaded_file is not None:
        return json.load(uploaded_file)
    
    # Si no, buscar localmente 'votos.json'
    if os.path.exists('votos.json'):
        with open('votos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# --- INTERFAZ PRINCIPAL ---
st.title("📊 Dashboard de Resultados Escolares")

# Sidebar para subir archivo si es necesario
st.sidebar.header("Cargar Datos")
uploaded_file = st.sidebar.file_uploader("Sube el archivo votos.json", type=['json'])
data = cargar_datos(uploaded_file)

if not data:
    st.warning("No se encontraron datos. Por favor asegúrate de que 'votos.json' esté en la carpeta o súbelo en el menú lateral.")
    st.stop()

st.sidebar.success(f"Datos cargados: {len(data)} votos")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏆 Valores", "🤝 Mejor Compañero", "📝 Datos Crudos"])

# --- ANÁLISIS VALORES ---
with tab1:
    st.header("Resultados por Valor")
    
    # Obtener lista de valores disponibles en los datos
    if len(data) > 0:
        valores_disponibles = list(data[0]['valores'].keys())
        valor_seleccionado = st.selectbox("Selecciona un Valor para ver el gráfico:", valores_disponibles)
        
        # Procesar votos para este valor
        conteo_valores = {}
        for voto in data:
            elegidos = voto['valores'].get(valor_seleccionado, [])
            for rut in elegidos:
                nombre = rut_a_nombre.get(rut, rut) # Traducir RUT a Nombre
                conteo_valores[nombre] = conteo_valores.get(nombre, 0) + 1
        
        if conteo_valores:
            df_valores = pd.DataFrame(list(conteo_valores.items()), columns=['Alumno', 'Votos'])
            df_valores = df_valores.sort_values('Votos', ascending=False)
            
            # Gráfico
            fig = px.bar(
                df_valores, 
                x='Alumno', 
                y='Votos', 
                color='Votos',
                title=f"Votos recibidos en: {valor_seleccionado}",
                text_auto=True,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay votos registrados para este valor aún.")

# --- ANÁLISIS MEJOR COMPAÑERO ---
with tab2:
    st.header("Ranking Mejor Compañero")
    st.markdown("""
    **Sistema de Puntaje:**
    * 🥇 1er Lugar: **3 Puntos**
    * 🥈 2do Lugar: **2 Puntos**
    * 🥉 3er Lugar: **1 Punto**
    """)
    
    ranking = {}
    
    for voto in data:
        elegidos = voto.get('mejor_companero', [])
        
        # Asignar puntos según posición en la lista (index 0 = 1er lugar)
        puntos_por_posicion = [3, 2, 1]
        
        for i, rut in enumerate(elegidos):
            if i < 3: # Solo consideramos los primeros 3 por seguridad
                nombre = rut_a_nombre.get(rut, rut)
                puntos = puntos_por_posicion[i]
                
                if nombre not in ranking:
                    ranking[nombre] = {'Votos Totales': 0, 'Puntaje': 0}
                
                ranking[nombre]['Votos Totales'] += 1
                ranking[nombre]['Puntaje'] += puntos

    if ranking:
        # Convertir a DataFrame
        df_ranking = pd.DataFrame.from_dict(ranking, orient='index').reset_index()
        df_ranking.columns = ['Alumno', 'Votos Totales', 'Puntaje']
        df_ranking = df_ranking.sort_values('Puntaje', ascending=False).reset_index(drop=True)
        
        # Mostrar tabla estilizada
        st.dataframe(
            df_ranking.style.background_gradient(cmap="Greens", subset=['Puntaje']),
            use_container_width=True
        )
        
        # Gráfico de Puntaje
        fig_ranking = px.bar(
            df_ranking.head(10), # Top 10
            x='Alumno',
            y='Puntaje',
            color='Puntaje',
            title="Top 10 - Puntaje Mejor Compañero",
            text_auto=True,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_ranking, use_container_width=True)
        
    else:
        st.info("No hay votos para Mejor Compañero aún.")

# --- DATOS CRUDOS ---
with tab3:
    st.write("Datos tal como vienen del archivo JSON:")
    st.json(data)
