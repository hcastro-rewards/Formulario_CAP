import streamlit as st

def mostrar():
    if st.session_state.gerencia_desbloqueada:
        st.title("📈 Dashboard Gerencial")
        st.success("Acceso autorizado. Bienvenido al panel de control de gerencia.")
        st.info("Aquí puedes integrar tus gráficos de Chart.js o gráficas nativas de Streamlit (Plotly, Altair).")
    else:
        st.error("Acceso denegado. Por favor, identifícate en el menú lateral.")
