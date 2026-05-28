# ui/quiz_view.py
import streamlit as st
from state.session import check_and_award_badges

def render_quiz_view():
    questions = st.session_state.questions

    if not questions:
        st.info("Aún no hay preguntas. ¡Genera una hoja de estudio primero!")
        return
    
    st.subheader(f"❓ Examen de Práctica: {st.session_state.topic}")
    st.caption(f"{len(questions)} preguntas generadas")

    for i, q in enumerate(questions):
        with st.expander(f"**P{i+1}: {q['question']}**", expanded=True):
            if i in st.session_state.revealed_answers:
                st.success(f"✅ **Respuesta: ** {q['answer']}")
            else:
                st.caption("Piénsalo primero, luego haz clic para revelar.")
                if st.button(f"Revelar Respuesta", key=f"reveal_{i}"):
                    st.session_state.revealed_answers.add(i)
                    st.session_state.milestones["questions_answered"] += 1
                    check_and_award_badges()
                    st.rerun()

    # Progress bar
    answered = len(st.session_state.revealed_answers)
    total = len(questions)
    st.divider()
    st.progress(answered / total if total > 0 else 0)
    st.caption(f"Reveladas {answered} de {total} respuestas")

    if answered == total and total > 0:
        st.balloons()
        st.success("🎉 ¡Repasaste todas las preguntas! ¡Excelente trabajo!")
        st.session_state.milestones["sessions_completed"] += 1
        check_and_award_badges()