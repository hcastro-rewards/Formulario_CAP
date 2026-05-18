import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# --- CONFIGURACION DE PAGINA CORPORATIVA ---
st.set_page_config(page_title="Rewards - Sistema de Rutas", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (MODO AZUL INTENSO) ---
st.markdown(
    """
    <style>
        .stApp { background-color: #072146; color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #004481 !important; }
        h1, h2, h3, h4, p, label { color: #FFFFFF !important; }
        
        /* Boton estado normal */
        div.stButton > button:first-child { background-color: #004481 !important; color: #FFFFFF !important; border: 2px solid #FFFFFF; border-radius: 8px; font-weight: bold; }
        
        /* Boton estado hover / seleccionado (Celeste con letra blanca) */
        div.stButton > button:first-child:hover, div.stButton > button:first-child:active, div.stButton > button:first-child:focus { 
            background-color: #3498db !important;
            color: #FFFFFF !important;
            border-color: #3498db !important; 
        }
        
        div[data-testid="stFileUploadDropzone"] div { color: #FFFFFF !important; }
        
        /* Ajuste para alertas y avisos */
        .stAlert[data-baseweb="alert"] { background-color: rgba(26, 188, 156, 0.2); color: #FFFFFF !important; border: 1px solid #1abc9c; }
        .stAlert[data-baseweb="alert-warning"] { background-color: rgba(241, 196, 15, 0.2); color: #FFFFFF !important; border: 1px solid #f1c40f; }
        .stAlert[data-baseweb="alert-error"] { background-color: rgba(231, 76, 60, 0.2); color: #FFFFFF !important; border: 1px solid #e74c3c; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- REEMPLAZO DEL TITULO POR EL LOGO DE REWARDS ---
URL_LOGO_REWARDS = "https://raw.githubusercontent.com/hcastro-rewards/Formulario_CAP/main/LOGO_REWARDS.png"

st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 10px;'>
        <img src='{URL_LOGO_REWARDS}' width='500' alt='Logo Rewards'>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>Sistema de Rutas Inteligente</p>", unsafe_allow_html=True)
st.divider()

# --- CONFIGURACION DE ENLACES EXTERNOS ---
ID_WEB_APP = "AKfycbzmhwXgNAGmoknSdl9rtaf2oNd93Ds_U_1CxleiuvZAmuK0iqwtHIEh4AgGR22gU139"
URL_BASE_GAS = f"https://script.google.com/macros/s/{ID_WEB_APP}/exec"
URL_BASE_DATOS_GS = "https://docs.google.com/spreadsheets/d/186GinOg7PgFcp1g9LAmW32K5vlTEK8ChYjI3qnsf1-4/edit?usp=sharing"

# --- FUNCIONES DE LIMPIEZA Y PROCESAMIENTO ---
def limpiar(valor):
    return "" if pd.isna(valor) else str(valor).strip()

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^A-Z0-9 ]", "", texto)
    return texto

def procesar_fila(fila, nombre_cap):
    marca = limpiar(fila.get("Marca"))
    direccion = limpiar(fila.get("Dirección"))
    distrito = limpiar(fila.get("Distrito"))
    kam = limpiar(fila.get("KAM"))
    psi = limpiar(fila.get("PSI"))
    puntos = limpiar(fila.get("Puntos BBVA"))
    tipo_local = limpiar(fila.get("Centro Comercial o P.C.")) 

    query = urllib.parse.quote(f"{marca} {direccion} {distrito} Lima Peru")

    maps_url = f"https://www.google.com/maps/search/{query}"
    google_url = f"https://www.google.com/search?q={query}"
    
    query_params = urllib.parse.urlencode({
        "comercio": marca,
        "dir": direccion,
        "kam": kam,
        "psi": psi,
        "puntos": puntos,
        "cap": nombre_cap,
        "tipo_local": tipo_local 
    })
    magic_link = f"{URL_BASE_GAS}?{query_params}"

    maps_text = f'=HYPERLINK("{maps_url}", "LINK MAPS")'
    google_text = f'=HYPERLINK("{google_url}", "LINK GOOGLE")'
    magic_text = f'=HYPERLINK("{magic_link}", "AUTO-RELLENO")'

    return pd.Series([maps_text, google_text, magic_text, maps_url, google_url, magic_link])

# --- CARGA DE BASE MAESTRA LOCAL ---
try:
    df_datos_base = pd.read_excel("data/Datos.xlsx", sheet_name="Datos")
except FileNotFoundError:
    st.error("No se encontro el archivo base 'Datos.xlsx' en la carpeta 'data'.")
    st.stop()

# --- GESTION DE SESION Y SINCRONIZACION EN VIVO ---
if 'dict_hojas' not in st.session_state:
    st.session_state['dict_hojas'] = None

if st.session_state['dict_hojas'] is None:
    st.info("El sistema esta listo para conectarse a la base de datos en la nube.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Iniciar Ruta", use_container_width=True):
            with st.spinner(" Sincronizando datos en vivo... esto puede tomar unos segundos."):
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_BASE_DATOS_GS)
                if match:
                    sheet_id = match.group(1)
                    excel_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                    try:
                        st.session_state['dict_hojas'] = pd.read_excel(excel_url, sheet_name=None)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Hubo un problema al descargar los datos: {e}")
                else:
                    st.error("El enlace de Google Sheet no es valido.")

# --- INTERFAZ PRINCIPAL ---
else:
    col_estado, col_boton = st.columns([3, 1])
    with col_estado:
        st.success(" Datos sincronizados correctamente. Trabajando en vivo.")
    with col_boton:
        if st.button(" Refrescar Datos"):
            st.session_state['dict_hojas'] = None
            st.rerun()
            
    st.divider()

    hoy = datetime.now().date()
    
    def obtener_fechas_validas(df):
        if df is None or 'Fecha' not in df.columns:
            return set()
        fechas = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        return set(fechas[fechas >= hoy].dropna().unique())

    df_pc_raw = st.session_state['dict_hojas'].get("PC 2026 - 2")
    df_cc_raw = st.session_state['dict_hojas'].get("CC 2026 - 2")
    df_cap_raw = st.session_state['dict_hojas'].get("CAPACITACIONES")

    fechas_todas = set()
    fechas_todas.update(obtener_fechas_validas(df_pc_raw))
    fechas_todas.update(obtener_fechas_validas(df_cc_raw))
    fechas_todas.update(obtener_fechas_validas(df_cap_raw))
    
    fechas_futuras = sorted(list(fechas_todas))

    if not fechas_futuras:
        st.warning("No hay rutas programadas para hoy o fechas futuras en ninguna de las bandejas.")
    else:
        fecha_sel = st.selectbox("Que fecha?", options=fechas_futuras, index=None)
        
        if fecha_sel:
            nombre_sel = st.radio(
                "Cual es tu nombre?", 
                options=["Augusto", "Gustavo", "Harold", "Ivan", "Mateo"],
                index=None
            )

            if nombre_sel:
                st.divider()
                st.subheader("Panel de Ruta Interactivo (Directo en Web)")
                st.info("Desliza hacia la derecha para encontrar los botones fijos de Visita y Maps.")
                
                encontro_datos = False 

                def mostrar_modulo(df_final, titulo):
                    st.markdown(f"### {titulo}")
                    st.success(f"Se encontraron {len(df_final)} locales para {titulo}.")
                    
                    columnas_generadas = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC']
                    df_final[columnas_generadas] = df_final.apply(lambda x: procesar_fila(x, nombre_sel), axis=1)

                    # --- CONFIGURACION DE AGGRID (Estilo Hibrido y Auto-ajustado) ---
                    gb = GridOptionsBuilder.from_dataframe(df_final)
                    
                    # 1. Ocultar columnas generadas que no se deben mostrar en la web
                    cols_to_hide = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_GOOGLE']
                    for col in cols_to_hide:
                        gb.configure_column(col, hide=True)

                    # 2. Configurar todas las columnas por defecto (sin filtros, sin menu, con tamaño de letra 13px)
                    gb.configure_default_column(
                        resizable=True, 
                        filter=False, 
                        sortable=False, 
                        suppressMenu=True,
                        cellStyle={'fontSize': '13px', 'whiteSpace': 'nowrap'} # Aplica 13px y fuerza a una sola linea
                    )

                    # 3. Asignar anchos minimos a columnas con texto largo para emular el comportamiento original (Opcion A)
                    gb.configure_column("Dire
