# app.py
import streamlit as st
from state.session import init_session_state
from ui.sidebar import render_sidebar
from ui.study_view import render_study_view
from ui.quiz_view import render_quiz_view
from ui.rewards_view import render_rewards_view

# -- Page config -- MUST be the very first Streamlit call
st.set_page_config(
    page_title="Compañero AI",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Initalize all session state
init_session_state()

# -- Header
st.title("🧑‍🏫 Compañero AI")
st.caption(
    "Tu tutor personal con IA. Sube tus apuntes o un PDF "
    "y obtén una hoja de estudio y preguntas de práctica en español."
)
st.divider()

# -- Sidebar (input and controls)
render_sidebar()

# -- Main content area
if st.session_state.study_sheet or st.session_state.questions:
    tab1, tab2, tab3 = st.tabs([
        "📄 Hoja de Estudio",
        "❓ Preguntas de Práctica",
        "🏆 Logros"
    ])
    with tab1:
        render_study_view()
    with tab2:
        render_quiz_view()
    with tab3:
        render_rewards_view()
else:
    # -- Empty state shown before first generation
    st.info(
        "👈 Ingresa tu tema y material en la barra lateral, "
        "luego haz clic en **Generar Hoja de Estudio** para comenzar."
    )
    st.markdown("### 📊 Tu progreso aparecerá aqui")
    st.markdown("- 📄 Hojas Generadas: -")
    st.markdown("- ❓ Preguntas Respondidas: -")
    st.markdown("- 🏆 Insignias: -")