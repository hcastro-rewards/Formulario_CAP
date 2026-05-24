import streamlit as st

def mostrar():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 40px; margin-top: 20px;'>
            <h1 style='color: #f8fafc; font-family: serif; font-weight: bold;'>Sistema Rutas Inteligente</h1>
            <p style='color: #94a3b8; font-size: 18px;'>Gestión centralizada de reporte de visitas, campañas y gerencia</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>📋</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #38bdf8; font-weight: bold;'>Reporte de Visitas</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Completar mantenimientos y evaluaciones en campo.</p>", unsafe_allow_html=True)
        if st.button("Ir a Visitas", use_container_width=True, key="btn_ir_visitas"):
            st.session_state.vista_actual = "Reporte de Visitas"
            st.session_state.last_cap = "Reporte de Visitas"
            st.session_state.last_ger = None
            st.rerun()

    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>📢</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #14b8a6; font-weight: bold;'>Reporte de Campañas</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Generar reportes y gestión de eventos masivos.</p>", unsafe_allow_html=True)
        if st.button("Ir a Campañas", use_container_width=True, key="btn_ir_campanas"):
            st.session_state.vista_actual = "Reporte de Campañas"
            st.session_state.last_cap = "Reporte de Campañas"
            st.session_state.last_ger = None
            st.rerun()

    with col3:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>📈</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #f59e0b; font-weight: bold;'>Dashboard Gerencial</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Métricas, gráficas y KPIs operativos de gerencia.</p>", unsafe_allow_html=True)
        if st.button("Ir a Dashboard", use_container_width=True, key="btn_ir_dashboard"):
            # Redirigimos directo. Si no tiene clave, el módulo Dashboard le pedirá ir a la barra lateral
            st.session_state.vista_actual = "Dashboard"
            st.session_state.last_ger = "Dashboard"
            st.session_state.last_cap = None
            st.rerun()