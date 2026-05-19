import streamlit as st
import pandas as pd
import urllib.parse
import unicodedata
import re
from datetime import datetime, timedelta
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

    # Extraer las hojas de datos
    df_pc_raw = st.session_state['dict_hojas'].get("PC 2026 - 2")
    df_cc_raw = st.session_state['dict_hojas'].get("CC 2026 - 2")
    df_cap_raw = st.session_state['dict_hojas'].get("CAPACITACIONES")

    # --- NUEVA LÓGICA DE FECHAS RELATIVAS ---
    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)
    manana = hoy + timedelta(days=1)

    # Creamos un diccionario para mostrar el texto bonito pero usar la fecha exacta por detrás
    opciones_fechas = {
        f"Ayer ({ayer.strftime('%Y-%m-%d')})": ayer,
        f"Hoy ({hoy.strftime('%Y-%m-%d')})": hoy,
        f"Mañana ({manana.strftime('%Y-%m-%d')})": manana
    }

    fecha_str = st.selectbox("Que fecha?", options=list(opciones_fechas.keys()), index=None)
    
    if fecha_str:
        # Recuperamos el objeto "date" real asociado a la selección del usuario
        fecha_sel = opciones_fechas[fecha_str]
        
        # --- AQUÍ SE AGREGÓ A FLOR EN LA LISTA FIJA ---
        nombre_sel = st.radio(
            "Cual es tu nombre?", 
            options=["Augusto", "Flor", "Gustavo", "Harold", "Ivan", "Mateo"],
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

                # --- CONFIGURACION DE AGGRID (Estilo Dataframe Nativo + Botones) ---
                gb = GridOptionsBuilder.from_dataframe(df_final)
                
                # 1. Ocultar columnas generadas e internas + Columnas innecesarias solicitadas para la Web
                cols_to_hide = [
                    'Link MAPS (Excel)', 'Link GOOGLE (Excel)', 'Auto-Relleno (Excel)', 'URL_GOOGLE',
                    'Indicaciones para Visitas', 'Fecha', 'CAP'
                ]
                for col in cols_to_hide:
                    gb.configure_column(col, hide=True)

                # 2. Configurar estilo por defecto: FUERZA UN ANCHO MINIMO PARA EVITAR QUE SE APLASTE EN MÓVIL
                gb.configure_default_column(
                    resizable=True, 
                    filter=False, 
                    sortable=False, 
                    suppressMenu=True,
                    suppressMovable=True, 
                    minWidth=180,  # <-- OBLIGA A LA PANTALLA A CREAR SCROLL HORIZONTAL
                    wrapText=True,
                    autoHeight=True,
                    cellStyle={'fontSize': '14px', 'whiteSpace': 'normal', 'padding': '10px 15px'} 
                )

                # 3. Inyeccion de JavaScript para botones HTML
                cell_renderer_btns = JsCode('''
                class BtnCellRenderer {
                    init(params) {
                        this.eGui = document.createElement('div');
                        this.eGui.style.display = 'flex';
                        this.eGui.style.alignItems = 'center';
                        this.eGui.style.justifyContent = 'center';
                        this.eGui.style.height = '100%';
                        
                        let label = params.colDef.headerName === "REPORTAR" ? "VISITA" : "MAPS";
                        let bgColor = params.colDef.headerName === "REPORTAR" ? "#004481" : "#3498db";
                        this.eGui.innerHTML = `
                         <a href="${params.value}" target="_blank" style="
                            display: inline-block;
                            width: 90%;
                            background-color: ${bgColor};
                            color: white;
                            text-align: center;
                            border-radius: 5px;
                            text-decoration: none;
                            font-weight: bold;
                            padding: 8px 0;
                            font-size: 12px;
                            line-height: 1;
                        ">${label}</a>
                        `;
                    }
                    getGui() {
                        return this.eGui;
                    }
                }
                ''')

                # 4. Configurar columnas de botones (fijas a la derecha con ancho rigido)
                gb.configure_column("URL_MAGIC", headerName="REPORTAR", cellRenderer=cell_renderer_btns, pinned='right', width=100, minWidth=100, maxWidth=100)
                gb.configure_column("URL_MAPS", headerName="UBICAR", cellRenderer=cell_renderer_btns, pinned='right', width=100, minWidth=100, maxWidth=100)

                # Ajustar la altura del encabezado para que quepa bien el texto si salta de linea
                gb.configure_grid_options(headerHeight=50, rowHeight=60) 
                
                gridOptions = gb.build()

                AgGrid(
                        df_final,
                        gridOptions=gridOptions,
                        allow_unsafe_jscode=True, 
                        fit_columns_on_grid_load=False, # Mantiene el scroll libre
                        theme='alpine' 
                )

                # --- EXPORTAR A EXCEL (CONSERVA LAS COLUMNAS OCULTAS DE LA WEB) ---
                df_excel = df_final.copy()
                
                # Definir únicamente las columnas de control técnico que deben limpiarse del Excel
                cols_a_eliminar = ['URL_MAPS', 'URL_GOOGLE', 'URL_MAGIC', 'Auto-Relleno (Excel)', '::auto_unique_id::']
                
                # Filtrar para eliminar solo las que existen y evitar errores
                cols_existentes = [col for col in cols_a_eliminar if col in df_excel.columns]
                df_excel = df_excel.drop(columns=cols_existentes)
                
                # Eliminar cualquier columna "sin nombre" (Unnamed) generada accidentalmente
                df_excel = df_excel.loc[:, ~df_excel.columns.str.contains('^Unnamed')]

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

            # --- MODULO 1: PUERTA CALLE ---
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

            # --- MODULO 2: CENTRO COMERCIAL ---
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

            # --- MODULO 3: CAPACITACIONES ---
            if df_cap_raw is not None and 'Fecha' in df_cap_raw.columns:
                df_cap = df_cap_raw.copy()
                df_cap['Fecha'] = pd.to_datetime(df_cap['Fecha'], errors='coerce').dt.date
                df_cap_filtrado = df_cap[(df_cap['Fecha'] == fecha_sel) & (df_cap['CAP'] == nombre_sel)].copy()
                
                if not df_cap_filtrado.empty:
                    encontro_datos = True
                    mostrar_modulo(df_cap_filtrado, "CAPACITACIONES")

            if not encontro_datos:
                # Alerta si no se encontraron datos para la fecha seleccionada
                st.warning(f"No tienes rutas ni capacitaciones asignadas para el {fecha_sel}.")
