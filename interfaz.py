import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA CORPORATIVA ---
st.set_page_config(page_title="Rewards - Sistema de Rutas", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (MODO AZUL INTENSO) ---
st.markdown(
    """
    <style>
        .stApp { background-color: #072146; color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #004481 !important; }
        h1, h2, h3, h4, p, label { color: #FFFFFF !important; }
        
        /* Botón estado normal */
        div.stButton > button:first-child { background-color: #004481 !important; color: #FFFFFF !important; border: 2px solid #FFFFFF; border-radius: 8px; font-weight: bold; }
        
        /* Botón estado hover / seleccionado (Celeste con letra blanca) */
        div.stButton > button:first-child:hover, div.stButton > button:first-child:active, div.stButton > button:first-child:focus { 
            background-color: #3498db !important; /* Color celeste */
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

# --- REEMPLAZO DEL TÍTULO POR EL LOGO DE REWARDS ---
URL_LOGO_REWARDS = "https://raw.githubusercontent.com/hcastro-rewards/Formulario_CAP/main/LOGO_REWARDS.png"

st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 10px;'>
        <img src='{URL_LOGO_REWARDS}' width='300' alt='Logo Rewards'>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>Sistema de Rutas Inteligente</p>", unsafe_allow_html=True)
st.divider()

# --- CONFIGURACIÓN DE ENLACES EXTERNOS ---
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
    st.error("No se encontró el archivo base 'Datos.xlsx' en la carpeta 'data'.")
    st.stop()

# --- GESTIÓN DE SESIÓN Y SINCRONIZACIÓN EN VIVO ---
if 'dict_hojas' not in st.session_state:
    st.session_state['dict_hojas'] = None

if st.session_state['dict_hojas'] is None:
    st.info("El sistema está listo para conectarse a la base de datos en la nube.")
    
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
                    st.error("El enlace de Google Sheet no es válido.")

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
        fecha_sel = st.selectbox("¿Qué fecha?", options=fechas_futuras, index=None)
        
        if fecha_sel:
            nombre_sel = st.radio(
                "¿Cuál es tu nombre?", 
                options=["Augusto", "Gustavo", "Harold", "Ivan", "Mateo"],
                index=None
            )

            if nombre_sel:
                st.divider()
                st.subheader("Panel de Ruta Interactivo (Directo en Web)")
                st.info("Haz clic en 'Abrir Formulario' directamente desde las tablas para reportar tu visita.")
                
                encontro_datos = False 

                def mostrar_modulo(df_final, titulo):
                    st.markdown(f"### 📍 {titulo}")
                    st.success(f"Se encontraron {len(df_final)} locales para {titulo}.")
                    
                    columnas_generadas = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC']
                    df_final[columnas_generadas] = df_final.apply(lambda x: procesar_fila(x, nombre_sel), axis=1)

                    st.dataframe(
                        df_final,
                        column_config={
                            "URL_MAGIC": st.column_config.LinkColumn("REPORTAR VISITA", display_text="Abrir Formulario"),
                            "URL_MAPS": st.column_config.LinkColumn("MAPS", display_text="Ir a Maps"),
                            "Link MAPS (Excel)": None,
                            "Link GOOGLE (Excel)": None,
                            "Auto-Relleno (Excel)": None,
                            "URL_GOOGLE": None
                        },
                        use_container_width=True,
                        hide_index=True
                    )

                    df_excel = df_final.drop(columns=['URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC'])
                    output = BytesIO()
                    df_excel.to_excel(output, index=False, engine='openpyxl')
                    st.download_button(
                        f"(Opcional) Descargar Excel - {titulo}",
                        data=output.getvalue(),
                        file_name=f"Ruta_{titulo.replace(' ', '_')}_{nombre_sel}_{fecha_sel}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"btn_{titulo}" 
                    )
                    st.divider()

                # --- MÓDULO 1: PUERTA CALLE ---
                if df_pc_raw is not None and 'Fecha' in df_pc_raw.columns:
                    df_pc = df_pc_raw.copy()
                    df_pc['Fecha'] = pd.to_datetime(df_pc['Fecha'], errors='coerce').dt.date
                    df_pc_filtrado = df_pc[(df_pc['Fecha'] == fecha_sel) & (df_pc['CAP'] == nombre_sel)].copy()
                    
                    if not df_pc_filtrado.empty:
                        encontro_datos = True
                        df_pc_filtrado['Centro Comercial o P.C.'] = "PUERTA CALLE"
                        
                        columnas_pc = ["KAM", "Marca", "PSI", "Puntos BBVA", "Centro Comercial o P.C.", "Dirección", "Distrito", "Indicaciones para Visitas", "Fecha", "CAP"]
                        for col in columnas_pc:
                            if col not in df_pc_filtrado.columns: df_pc_filtrado[col] = ""
                        df_pc_filtrado = df_pc_filtrado[columnas_pc]
                        
                        mostrar_modulo(df_pc_filtrado, "PUERTA CALLE")

                # --- MÓDULO 2: CENTRO COMERCIAL ---
                if df_cc_raw is not None and 'Fecha' in df_cc_raw.columns:
                    df_cc = df_cc_raw.copy()
                    df_cc['Fecha'] = pd.to_datetime(df_cc['Fecha'], errors='coerce').dt.date
                    df_cc_filtrado = df_cc[(df_cc['Fecha'] == fecha_sel) & (df_cc['CAP'] == nombre_sel)].copy()
                    
                    if not df_cc_filtrado.empty:
                        encontro_datos = True
                        if "Centro Comercial o P.C." in df_cc_filtrado.columns:
                            df_cc_filtrado['Centro Comercial_norm'] = df_cc_filtrado['Centro Comercial o P.C.'].apply(normalizar_texto)
                            df_datos = df_datos_base.copy()
                            df_datos['Centro Comercial_norm'] = df_datos['Centro Comercial'].apply(normalizar_texto)

                            columnas_a_borrar = [col for col in ['Dirección', 'Distrito'] if col in df_cc_filtrado.columns]
                            if columnas_a_borrar:
                                df_cc_filtrado = df_cc_filtrado.drop(columns=columnas_a_borrar)

                            df_cc_filtrado = df_cc_filtrado.merge(
                                df_datos[['Centro Comercial_norm', 'Dirección', 'Distrito']],
                                on='Centro Comercial_norm',
                                how='left'
                            )
                            df_cc_filtrado = df_cc_filtrado.drop(columns=['Centro Comercial_norm'])
                        
                        columnas_cc = ["KAM", "Marca", "PSI", "Puntos BBVA", "Centro Comercial o P.C.", "Dirección", "Distrito", "Indicaciones para Visitas", "Fecha", "CAP"]
                        for col in columnas_cc:
                            if col not in df_cc_filtrado.columns: df_cc_filtrado[col] = ""
                        df_cc_filtrado = df_cc_filtrado[columnas_cc]

                        mostrar_modulo(df_cc_filtrado, "CENTRO COMERCIAL")

                # --- MÓDULO 3: CAPACITACIONES ---
                if df_cap_raw is not None and 'Fecha' in df_cap_raw.columns:
                    df_cap = df_cap_raw.copy()
                    df_cap['Fecha'] = pd.to_datetime(df_cap['Fecha'], errors='coerce').dt.date
                    df_cap_filtrado = df_cap[(df_cap['Fecha'] == fecha_sel) & (df_cap['CAP'] == nombre_sel)].copy()
                    
                    if not df_cap_filtrado.empty:
                        encontro_datos = True
                        mostrar_modulo(df_cap_filtrado, "CAPACITACIONES")

                if not encontro_datos:
                    st.warning(f"No tienes rutas ni capacitaciones asignadas para el {fecha_sel}.")
