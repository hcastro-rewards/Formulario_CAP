import streamlit as st

# Marcador de posición para el enlace de Google Apps Script
URL_BASE_APP_SCRIPT = "https://script.google.com/macros/s/AKfycby_wgLWvsNvS0Jw-NFt-vWHmb7HEMBgzA_oKdgmJAnCYYxxem-X1UfjQ7ySZJ0NeyET/exec"
def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        # Nuevo título para la vista
        st.markdown("<h1 style='font-size: 32px; color: #f8fafc; margin-top: 0px;'>Multiplicador de codigos</h1>", unsafe_allow_html=True)
    with col_volver:
        st.write("")
        # Se cambia el key del botón para evitar duplicidad en Streamlit
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_backoffice"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
            
    # Nuevo subtítulo
    st.markdown("<p style='color: #94a3b8; font-size: 18px; margin-top: -10px;'>Generar multiplicador de codigos.</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Nuevos textos descriptivos y en el botón
        st.info(" Haz clic en el botón inferior para abrir generador de codigos.")
        st.link_button(" ABRIR GENERADOR DE CODIGOS", url=URL_BASE_APP_SCRIPT, use_container_width=True)