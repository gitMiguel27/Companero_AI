# ui/sidebar.py
import os
import streamlit as st
from dotenv import load_dotenv
from core.study_sheet import (
    generate_study_sheet,
    generate_study_sheet_from_pdf,
    generate_from_memory,
    auto_detect_topic,
)
from core.questions import generate_questions, generate_questions_from_memory
from memory.vector_store import get_stored_topics
from state.session import check_and_award_badges

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

def render_sidebar():
    with st.sidebar:
        st.header("🎯 ¿Qué estás estudiando?")

        # -- Topic Input
        topic = st.text_input(
            "Tema",
            placeholder="ej. Fotosíntesis, La Revolución Mexicana, Educaciones Cuadráticas",
            key="topic_input"
        )

        st.divider()

        # -- Input mode selector
        input_mode = st.radio(
            "¿Cómo quieres ingresar tu material?",
            options=["Escribir / Pegar texto", "Subir PDF", "Usar tema guardado"],
            key="input_mode_radio"
        )

        content = ""
        file_path = None

        # -- Mode: type/paste text
        if input_mode == "Escribir / Pegar texto":
            content = st.text_area(
                "Pega tus apuntes aquí",
                placeholder="Pega el texto de tu libro, tus notas de clase o cualquier material...",
                height=220,
                key="content_input"
            )
        
        # -- Mode: upload PDF
        elif input_mode == "Subir PDF":
            uploaded_file = st.file_uploader(
                "Sube tu PDF",
                type=["pdf"],
                key="pdf_uploader"
            )
            if uploaded_file:
                # Save to disk so pdfplumber can access it
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"✅ {uploaded_file.name} cargado")

        # -- Mode: use past memory
        elif input_mode == "Usar tema guardado":
            stored_topics = get_stored_topics()
            if stored_topics:
                selected = st.selectbox(
                    "Elige un tema guardado",
                    options=stored_topics,
                    key="memory_topic_select"
                )
                if selected:
                    topic = selected
                    st.session_state.use_memory = True
            else:
                st.info("Aún no tienes temas guardados. ¡Sube material primero!")

        # -- Number of questions
        st.divider()
        num_questions = st.slider(
            "Número de preguntas de práctica",
            min_value=3, max_value=10, value=5,
            key="num_questions"
        )

        # -- Auto-detect topic button
        if content and not topic:
            if st.button("🔍 Detectar tema automáticamente", use_container_width=True):
                with st.spinner("Detectando tema..."):
                    detected = auto_detect_topic(content)
                    st.session_state.topic = detected
                    st.rerun()
        
        # -- Main generate button
        can_generate = bool(
            (content and content.strip()) or
            file_path or
            st.session_state.get("use_memory")
        )

        if st.button(
            "✨ Generar Hoja de Estudio",
            disabled=not can_generate,
            use_container_width=True,
            type="primary"
        ):
            _handle_generate(topic, content, file_path, num_questions)

        if not can_generate:
            st.caption("⬆️ Ingresa material de estudio para comenzar.")

def _handle_generate(topic: str, content: str, file_path: str, num_questions: int):
    """
    Orchestrates study sheet + questions generation based on input mode."""

    # Reset memory flag whenever a new generation is triggered
    if file_path or content:
        st.session_state.use_memory = False

    use_memory = st.session_state.get("use_memory", False)

    with st.spinner("Generando tu hoja de estudio en español..."):
        if use_memory:
            study_sheet = generate_from_memory(topic)
            questions = generate_questions_from_memory(topic, num_questions)
            st.session_state.use_memory = False

        elif file_path:
            study_sheet, pdf_content = generate_study_sheet_from_pdf(topic, file_path)

            # Guard against empty pdf_content on first run
            # ChromaDB embedding model may not be fully loaded yet
            if not pdf_content or len(pdf_content) < 50:
                st.warning("⚠️ Reintentando generación de preguntas...")
                study_sheet, pdf_content = generate_study_sheet_from_pdf(topic, file_path)

            questions = generate_questions(topic, pdf_content, num_questions)
            st.session_state.milestones["pdfs_uploaded"] += 1

        else:
            study_sheet = generate_study_sheet(topic, content)
            questions = generate_questions(topic, content, num_questions)

    st.session_state.study_sheet = study_sheet
    st.session_state.questions = questions
    st.session_state.topic = topic
    st.session_state.raw_content = content
    st.session_state.revealed_answers = set()
    st.session_state.milestones["study_sheets_generated"] += 1

    check_and_award_badges()
    st.success("✅ Listo! Revisa las pestañas arriba.")
