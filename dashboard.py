import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Resultados Votación - Curso 2", layout="wide")

# --- DATOS DE ESTUDIANTES (LISTA 2 - Actualizada) ---
ESTUDIANTES = [
    {"rut": "241035387", "nombre": "LEA ACUÑA"},
    {"rut": "242058143", "nombre": "ANDRES ALOMAR"},
    {"rut": "24001632K", "nombre": "EMILIA ALVAREZ"},
    {"rut": "239604099", "nombre": "PALOMA ASTORGA"},
    {"rut": "241983889", "nombre": "DOMINGA CACERES"},
    {"rut": "238721709", "nombre": "VALENTIN CALLEJA"},
    {"rut": "241730395", "nombre": "MARÍA CARTER"},
    {"rut": "242082257", "nombre": "FELIPE CASTRO"},
    {"rut": "239490794", "nombre": "GADIR CHACOFF"},
    {"rut": "239790070", "nombre": "FERNANDO CHAMORRO"},
    {"rut": "239154379", "nombre": "PEDRO ESCOBAR"},
    {"rut": "239780059", "nombre": "IGNACIO FERRADA"},
    {"rut": "241914259", "nombre": "AURORA GUTIERREZ"},
    {"rut": "239703275", "nombre": "MARTIN HERRERA"},
    {"rut": "239899935", "nombre": "JUAN CRISTOBAL JULIO"},
    {"rut": "239768210", "nombre": "AISHA KUZHITHATTIL"},
    {"rut": "23922010K", "nombre": "GABRIELA LEIVA"},
    {"rut": "24050958K", "nombre": "VIOLETA LETELIER"},
    {"rut": "238896975", "nombre": "JOSEFINA MARIN"},
    {"rut": "241195767", "nombre": "SOFIA MAUREIRA"},
    {"rut": "241053091", "nombre": "JAVIER MUCI"},
    {"rut": "241456765", "nombre": "POLO MUÑOZ"},
    {"rut": "24216072K", "nombre": "CONSTANZA PIÑA"},
    {"rut": "239832792", "nombre": "MIA RENCK"},
    {"rut": "239737730", "nombre": "CATALINA ROMERO"},
    {"rut": "24007415K", "nombre": "ANTONIA SABANDO"},
    {"rut": "239398987", "nombre": "MAX TREWHELA"},
    {"rut": "239670717", "nombre": "FERRAN XARLES"}
]

# Crear diccionario para búsqueda rápida RUT -> Nombre
rut_a_nombre = {e['rut']: e['nombre'] for e in ESTUDIANTES}

# --- FUNCIÓN DE CARGA LOCAL ---
def cargar_datos_locales(uploaded_file=None):
    # Prioridad 1: Archivo subido manualmente (por si quieres analizar un backup)
    if uploaded_file is not None:
        return json.load(uploaded_file), "Archivo subido manualmente"
    
    # Prioridad 2: Archivo local generado por el programa de votación
    archivo_local = 'votos.json'
    if os.path.exists(archivo_local):
        with open(archivo_local, 'r', encoding='utf-8') as f:
            return json.load(f), f"Archivo local '{archivo_local}'"
            
    return [], None

# --- INTERFAZ PRINCIPAL ---
st.title("📊 Dashboard Curso 2 (Local)")

# Sidebar simplificado
st.sidebar.header("Fuente de Datos")
uploaded_file = st.sidebar.file_uploader("Opcional: Subir JSON externo", type=['json'])

# Cargar datos
data, fuente = cargar_datos_locales(uploaded_file)

if not data:
    st.error("❌ No se encontraron datos.")
    st.info("Asegúrate de que el archivo 'votos.json' esté en la misma carpeta que este script, o súbelo en el menú lateral.")
    st.stop()

st.success(f"✅ Datos cargados desde: {fuente} ({len(data)} votos)")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏆 Valores", "🤝 Mejor Compañero", "📝 Datos Crudos"])

# --- ANÁLISIS VALORES ---
with tab1:
    st.header("Resultados por Valor")
    if len(data) > 0:
        # Extraer todos los valores posibles de los datos
        valores_encontrados = set()
        for voto in data:
            if 'valores' in voto:
                valores_encontrados.update(voto['valores'].keys())
        
        valores_disponibles = list(valores_encontrados)
        
        if valores_disponibles:
            valor_seleccionado = st.selectbox("Selecciona un Valor:", valores_disponibles)
            
            conteo_valores = {}
            for voto in data:
                elegidos = voto['valores'].get(valor_seleccionado, [])
                for rut in elegidos:
                    nombre = rut_a_nombre.get(rut, rut)
                    conteo_valores[nombre] = conteo_valores.get(nombre, 0) + 1
            
            if conteo_valores:
                df_valores = pd.DataFrame(list(conteo_valores.items()), columns=['Alumno', 'Votos'])
                df_valores = df_valores.sort_values('Votos', ascending=False)
                
                fig = px.bar(
                    df_valores, 
                    x='Alumno', y='Votos', color='Votos',
                    title=f"Votos en: {valor_seleccionado}",
                    text_auto=True, color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin votos para este valor.")
        else:
            st.warning("El archivo JSON no parece tener estructura de 'valores'.")
    else:
        st.info("El archivo está vacío.")

# --- ANÁLISIS MEJOR COMPAÑERO ---
with tab2:
    st.header("Ranking Mejor Compañero")
    ranking = {}
    
    for voto in data:
        elegidos = voto.get('mejor_companero', [])
        puntos_por_posicion = [3, 2, 1]
        
        for i, rut in enumerate(elegidos):
            if i < 3:
                nombre = rut_a_nombre.get(rut, rut)
                puntos = puntos_por_posicion[i]
                
                if nombre not in ranking:
                    ranking[nombre] = {'Votos Totales': 0, 'Puntaje': 0}
                ranking[nombre]['Votos Totales'] += 1
                ranking[nombre]['Puntaje'] += puntos

    if ranking:
        df_ranking = pd.DataFrame.from_dict(ranking, orient='index').reset_index()
        df_ranking.columns = ['Alumno', 'Votos Totales', 'Puntaje']
        df_ranking = df_ranking.sort_values('Puntaje', ascending=False).reset_index(drop=True)
        
        st.dataframe(df_ranking.style.background_gradient(cmap="Greens", subset=['Puntaje']), use_container_width=True)
        
        fig_ranking = px.bar(
            df_ranking.head(10),
            x='Alumno', y='Puntaje', color='Puntaje',
            title="Top 10 - Puntaje Mejor Compañero",
            text_auto=True, color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_ranking, use_container_width=True)
    else:
        st.info("No hay datos de Mejor Compañero.")

# --- DATOS CRUDOS ---
with tab3:
    st.write(f"Viendo datos de: {len(data)} estudiantes")
    st.json(data)
