import streamlit as st
import vistas.inicio as inicio
import vistas.reporte_visitas as reporte_visitas
import vistas.reporte_campanas as reporte_campanas
import vistas.dashboard as dashboard

# --- CONFIGURACIÓN DE PÁGINA CORPORATIVA ---
st.set_page_config(page_title="Portal Operativo Integrado", layout="wide", initial_sidebar_state="expanded")

# --- CARGAR ESTILOS CSS ---
def cargar_css(archivo):
    try:
        with open(archivo, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Si no encuentra el CSS, ignora el error

cargar_css("assets/estilos.css")

# --- VARIABLES GLOBALES ---
URL_LOGO_REWARDS = "https://raw.githubusercontent.com/hcastro-rewards/Formulario_CAP/main/LOGO_REWARDS.png"
CLAVE_GERENCIA = "GER123" # Cambia esto por tu contraseña real

# --- INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = 'Inicio'
if 'gerencia_desbloqueada' not in st.session_state:
    st.session_state.gerencia_desbloqueada = False
if 'dict_hojas' not in st.session_state:
    st.session_state['dict_hojas'] = None

# --- MODAL DE SEGURIDAD (STREAMLIT DIALOG) ---
@st.dialog("🔒 Acceso Restringido - Gerencia")
def modal_seguridad():
    st.write("Ingresa la clave de autorización para ver el Dashboard y módulos gerenciales.")
    clave = st.text_input("Contraseña", type="password", placeholder="••••••")
    
    if st.button("DESBLOQUEAR", use_container_width=True):
        if clave == CLAVE_GERENCIA:
            st.session_state.gerencia_desbloqueada = True
            st.session_state.vista_actual = 'Dashboard'
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")

# --- MENÚ LATERAL (BARRA DE NAVEGACIÓN) ---
with st.sidebar:
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><img src='{URL_LOGO_REWARDS}' width='100%'></div>", unsafe_allow_html=True)
    
    # 1. Inicio (Botón Libre)
    if st.button(" Inicio"):
        st.session_state.vista_actual = 'Inicio'
        
    # --- SECCIÓN CAPACITADOR (ACORDEÓN PLANO 1) ---
    with st.expander(" CAPACITADOR", expanded=True):
        
        if st.button("Reporte de Visitas"):
            st.session_state.vista_actual = 'Reporte Visitas'
            
        if st.button("Reporte de Campañas"):
            st.session_state.vista_actual = 'Reporte Campañas'
            
    # --- SECCIÓN GERENCIA (ACORDEÓN PLANO 2) ---
    with st.expander(" GERENCIA", expanded=False):
        
        if st.button("Dashboard"):
            if not st.session_state.gerencia_desbloqueada:
                modal_seguridad()
            else:
                st.session_state.vista_actual = 'Dashboard'

# --- ENRUTAMIENTO DE VISTAS ---
if st.session_state.vista_actual == 'Inicio':
    inicio.mostrar()
elif st.session_state.vista_actual == 'Reporte Visitas':
    reporte_visitas.mostrar()
elif st.session_state.vista_actual == 'Reporte Campañas':
    reporte_campanas.mostrar()
elif st.session_state.vista_actual == 'Dashboard':
    dashboard.mostrar()
