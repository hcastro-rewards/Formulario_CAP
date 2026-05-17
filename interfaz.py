import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA CORPORATIVA ---
st.set_page_config(page_title="Rewards - Sistema de Rutas", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS CSS PERSONALIZADOS (MODO CLARO / MINIMALISTA) ---
st.markdown(
    """
    <style>
        /* Fondo claro perla para la aplicación */
        .stApp { background-color: #F4F7F6; }
        
        /* Títulos y textos generales */
        h1, h2, h3, p, label { color: #002B5B !important; font-family: 'Georgia', serif; }
        .stMarkdown p { color: #475569 !important; font-family: 'Arial', sans-serif; }
        
        /* Modificación del Botón Primario (Azul grande) */
        button[kind="primary"] {
            background-color: #1A365D !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            padding: 15px !important;
            border: none !important;
            transition: all 0.3s ease;
        }
        button[kind="primary"]:hover {
            background-color: #2B6CB0 !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
        }

        /* Modificación del Botón Secundario (Cambiar técnico / Refrescar) */
        button[kind="secondary"] {
            background-color: white !important;
            color: #475569 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }
        button[kind="secondary"]:hover {
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
        }
        
        /* Ocultar el índice por defecto de las tablas de Streamlit para más limpieza */
        [data-testid="stTable"] { background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05); }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNCIÓN PARA DIBUJAR LA BARRA DE PROGRESO (STEPPER) ---
def dibujar_stepper(paso_actual):
    c1_bg, c1_txt = ("#1A365D", "white") if paso_actual >= 1 else ("#E2E8F0", "#64748B")
    c2_bg, c2_txt = ("#1A365D", "white") if paso_actual >= 2 else ("#E2E8F0", "#64748B")
    
    html_stepper = f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem; margin-top: 1rem; font-family: Arial, sans-serif;">
        <div style="text-align: center; position: relative; z-index: 1;">
            <div style="width: 35px; height: 35px; border-radius: 50%; background-color: {c1_bg}; color: {c1_txt}; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">1</div>
            <div style="font-size: 0.75rem; font-weight: bold; color: {c1_bg}; letter-spacing: 1px;">INICIO</div>
        </div>
        
        <div style="height: 2px; background-color: #E2E8F0; width: 120px; margin: 0 15px; position: relative; top: -12px; z-index: 0;"></div>
        
        <div style="text-align: center; position: relative; z-index: 1;">
            <div style="width: 35px; height: 35px; border-radius: 50%; background-color: {c2_bg}; color: {c2_txt}; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">2</div>
            <div style="font-size: 0.75rem; font-weight: bold; color: {c2_bg}; letter-spacing: 1px;">REGISTRO</div>
        </div>
    </div>
    """
    st.markdown(html_stepper, unsafe_allow_html=True)

# --- REEMPLAZO DEL TÍTULO POR EL LOGO DE REWARDS ---
URL_LOGO_REWARDS = "https://raw.githubusercontent.com/hcastro-rewards/Formulario_CAP/main/LOGO_REWARDS.png"

st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 5px; margin-top: 10px;'>
        <img src='{URL_LOGO_REWARDS}' width='250' alt='Logo Rewards'>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("<h2 style='text-align: center; color: #1A365D; margin-top: 0;'>Registro de Visitas Técnicas</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 1rem; margin-bottom: 2rem;'>Completa los datos de tu visita de forma rápida y ordenada</p>", unsafe_allow_html=True)
st.divider()

# --- INICIALIZAR VARIABLES DE ESTADO (Para movernos entre pasos) ---
if 'step' not in st.session_state:
    st.session_state['step'] = 1
if 'fecha_sel' not in st.session_state:
    st.session_state['fecha_sel'] = None
if 'nombre_sel' not in st.session_state:
    st.session_state['nombre_sel'] = None
if 'dict_hojas' not in st.session_state:
    st.session_state['dict_hojas'] = None

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

# --- FLUJO DE APLICACIÓN ---
if st.session_state['dict_hojas'] is None:
    # ESTADO INICIAL: No hay datos sincronizados
    st.info("El sistema está listo para conectarse a la base de datos en la nube.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Descargar y Sincronizar Datos", type="primary", use_container_width=True):
            with st.spinner("Sincronizando datos en vivo... esto puede tomar unos segundos."):
                match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_BASE_DATOS_GS)
                if match:
                    sheet_id = match.group(1)
                    excel_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
                    try:
                        st.session_state['dict_hojas'] = pd.read_excel(excel_url, sheet_name=None)
                        st.session_state['step'] = 1 # Pasamos automáticamente al Paso 1
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Hubo un problema al descargar los datos: {e}")
                else:
                    st.error("El enlace de Google Sheet no es válido.")

else:
    # --- PROCESAR FECHAS GLOBALES ---
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
        st.stop()

    # =========================================================
    # PASO 1: IDENTIFICACIÓN (Elegir Fecha y Nombre)
    # =========================================================
    if st.session_state['step'] == 1:
        dibujar_stepper(1)
        
        # Tarjeta visual usando columnas para centrar
        _, col_card, _ = st.columns([1, 3, 1])
        
        with col_card:
            st.markdown("### Identificación")
            st.markdown("Selecciona tu fecha de ruta y tu nombre para continuar.")
            
            # Selectores juntos
            fecha_temp = st.selectbox("FECHA ASIGNADA *", options=fechas_futuras, index=None)
            nombre_temp = st.selectbox(
                "SELECCIONA TU NOMBRE *", 
                options=["Augusto", "Gustavo", "Harold", "Ivan", "Mateo"],
                index=None
            )
            
            st.write("") # Espaciador
            
            # Botón Primario para avanzar
            if st.button("Ver mis registros pendientes", type="primary", use_container_width=True):
                if fecha_temp and nombre_temp:
                    st.session_state['fecha_sel'] = fecha_temp
                    st.session_state['nombre_sel'] = nombre_temp
                    st.session_state['step'] = 2
                    st.rerun()
                else:
                    st.error("⚠️ Por favor, completa la Fecha y el Nombre para continuar.")

    # =========================================================
    # PASO 2: REGISTRO (Visualizar Tablas Modulares)
    # =========================================================
    elif st.session_state['step'] == 2:
        dibujar_stepper(2)
        
        # Recuperamos variables del estado
        fecha_sel = st.session_state['fecha_sel']
        nombre_sel = st.session_state['nombre_sel']

        # Encabezado del paso 2
        st.markdown(f"### Registros pendientes")
        st.markdown(f"Mostrando información de ruta para **{nombre_sel}** en la fecha **{fecha_sel}**.")
        
        encontro_datos = False 

        # --- Función interna para renderizar tablas modulares en Modo Claro ---
        def mostrar_modulo(df_final, titulo):
            st.markdown(f"#### 📍 {titulo}")
            
            columnas_generadas = ['Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC']
            df_final[columnas_generadas] = df_final.apply(lambda x: procesar_fila(x, nombre_sel), axis=1)

            st.dataframe(
                df_final,
                column_config={
                    "URL_MAGIC": st.column_config.LinkColumn("REPORTAR VISITA", display_text="Completar Formulario"),
                    "URL_MAPS": st.column_config.LinkColumn("MAPS", display_text="Ver Mapa"),
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
                f"Descargar Backup Excel - {titulo}",
                data=output.getvalue(),
                file_name=f"Ruta_{titulo.replace(' ', '_')}_{nombre_sel}_{fecha_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"btn_{titulo}",
                type="secondary"
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
            st.info(f"No tienes rutas ni capacitaciones asignadas para el {fecha_sel}.")

        # --- BOTÓN PARA REGRESAR AL PASO 1 ---
        st.write("")
        _, col_back, _ = st.columns([1, 2, 1])
        with col_back:
            if st.button("← Cambiar técnico", type="secondary", use_container_width=True):
                st.session_state['step'] = 1
                st.rerun()
