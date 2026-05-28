# ui/study_view.py
import streamlit as st

def render_study_view():
    if not st.session_state.study_sheet:
        st.info("Aún no hay hoja de estudio. ¡Genera una desde la barra lateral!")
        return
    
    st.subheader(f"📄 Hoja de Estudio: {st.session_state.topic}")
    st.markdown(st.session_state.study_sheet)
    st.divider()

    # Download button - students can save and print their study sheet
    st.download_button(
        label="⬇️ Descargar Hoja de Estudio",
        data=st.session_state.study_sheet,
        file_name=f"hoja_estudio_{st.session_state.topic.replace(' ', '_')}.md",
        mime="text/markdown",
    )