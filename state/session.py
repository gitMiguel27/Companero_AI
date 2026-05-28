# state/session.py
import streamlit as st

def init_session_state():
    """
    Initializes all sessions state variables used acroos the app.

    Streamlit re-runs the entire script on every user interaction. Session state is how we persist data (like a generated study sheet) between those re-runs without losing it.

    Call this at the very top of app.py before any rendering.
    """
    defaults = {
        "topic": "",
        "raw_content": "",
        "study_sheet": None,
        "questions": [],
        "revealed_answers": set(),
        "input_mode": "text",   # "text" or "pdf"
        "use_memory": False,    # True if loading from past session
        "milestones": {
            "study_sheets_generated": 0,
            "questions_answered": 0,
            "sessions_completed": 0,
            "pdfs_uploaded": 0,
        },
        "badges_earned": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_and_award_badges():
    """
    Evaluates current milestone counts and awards new badges. Displays a toast notification for each newly earned badge.

    Add new rules to the `rules` list to add new badge types.
    """
    m = st.session_state.milestones
    earned = st.session_state.badges_earned

    rules = [
        (m["study_sheets_generated"] >= 1, "Primera Hoja de Estudio", "📄"),
        (m["study_sheets_generated"] >= 5, "Máquina de Estudio", "🚀"),
        (m["questions_answered"] >=5, "Primer Examen", "🎯"),
        (m["questions_answered"] >= 20, "Campeón de Exámenes", "🏆"),
        (m["sessions_completed"] >= 3, "Estudiante Constante", "🔥"),
        (m["pdfs_uploaded"] >= 1, "Primer PDF", "📚")
    ]

    for condition, badge_name, emoji in rules:
        if condition and badge_name not in earned:
            earned.append(badge_name)
            st.toast(f"{emoji} ¡Insignia desbloqueda: **{badge_name}**!", icon=emoji)
