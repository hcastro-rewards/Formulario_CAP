import streamlit as st

# DEBES PEGAR AQUÍ LA URL COMPLETA DE TU WEB APP DE APPS SCRIPT
# Ejemplo: "https://script.google.com/macros/s/AKfycb.../exec"
URL_BASE_APP_SCRIPT = "https://script.google.com/macros/s/AKfycbyZObX6vBV2ZgkRcyiPoYlKe4IfMqx6ik1lMoDSDhovuEMFytjm0uaVFdHwTLsrGWtG/exec" 

def mostrar():
    st.title(" Reporte de Campañas")
    st.markdown("<p style='color: #94a3b8;'>Genera un nuevo reporte de campaña para la base de datos.</p>", unsafe_allow_html=True)
    st.divider()

    # Construimos la URL agregando el parámetro ?tipo=campana
    url_campana = f"{URL_BASE_APP_SCRIPT}?tipo=campana"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(" Haz clic en el botón inferior para abrir el formulario.")
        
        # Este botón usa la función nativa de Streamlit para abrir enlaces
        st.link_button(
            " ABRIR FORMULARIO DE CAMPAÑA", 
            url=url_campana, 
            use_container_width=True
        )