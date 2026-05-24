import streamlit as st

URL_BASE_APP_SCRIPT = "https://script.google.com/macros/s/AKfycbyZObX6vBV2ZgkRcyiPoYlKe4IfMqx6ik1lMoDSDhovuEMFytjm0uaVFdHwTLsrGWtG/exec" 

def mostrar():
    col_titulo, col_volver = st.columns([4, 1])
    with col_titulo:
        st.title("Reporte de Campañas")
    with col_volver:
        st.write("")
        if st.button("← Volver al Inicio", use_container_width=True, key="volver_campanas"):
            st.session_state.vista_actual = 'Inicio'
            st.session_state.last_cap = None
            st.session_state.last_ger = None
            st.rerun()
            
    st.markdown("<p style='color: #94a3b8;'>Genera un nuevo reporte de campaña para la base de datos.</p>", unsafe_allow_html=True)
    st.divider()

    url_campana = f"{URL_BASE_APP_SCRIPT}?tipo=campana"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(" Haz clic en el botón inferior para abrir el formulario.")
        st.link_button(" ABRIR FORMULARIO DE CAMPAÑA", url=url_campana, use_container_width=True)