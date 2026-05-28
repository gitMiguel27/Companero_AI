# ui.rewards_view.py
import streamlit as st

BADGE_CATALOG = {
    "Primera Hoja de Estudio": {
        "emoji": "📄",
        "descripcion": "Generaste tu primera hoja de estudio.",
        "tip": "¡Sigue adelante - genera 5 para desbloquear Máquina de Estudio!"
    },
    "Máquina de Estudio": {
        "emoji": "🚀",
        "descripcion": "Generaste 5 hojas de estudio.",
        "tip": "¡Eres imparable!"
    },
    "Primer PDF": {
        "emoji": "📚",
        "descripcion": "Subiste tu primer PDF.",
        "tip": "Prueba con diferentes materiales para aprovechar al máximo."
    },
    "Primer Examen": {
        "emoji": "🎯",
        "descripcion": "Revelaste 5 respuestas de práctica.",
        "tip": "¡Sigue - 20 respuestas te dan el Campeón de Exámenes!"
    },
    "Campeón de Exámenes": {
        "emoji": "🏆",
        "descripcion": "Revelaste 20 respuestas.",
        "tip": "¡Dedicaión extraordinaria!"
    },
    "Estudiante Constante": {
        "emoji": "🔥",
        "descripcion": "Completaste 3 sesiones de estudio.",
        "tip": "La consistencia es la clave del dominio."
    },
}

def render_rewards_view():
    st.subheader("🏆 Tu Progreso")
    m = st.session_state.milestones
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Hojas Generadas", m["study_sheets_generated"])
    col2.metric("❓ Preguntas Respondidas", m["questions_answered"])
    col3.metric("✅ Sesiones Completadas", m["sessions_completed"])
    col4.metric("📚 PDFs Subidos", m["pdfs_uploaded"])

    st.divider()
    earned = st.session_state.badges_earned

    if earned:
        st.subheader("🎖️ Insignias Ganadas")
        cols = st.columns(min(len(earned), 3))
        for i, badge_name in enumerate(earned):
            badge = BADGE_CATALOG.get(badge_name, {})
            with cols[i % 3]:
                st.markdown(f"### {badge.get('emoji', '⭐')} {badge_name}")
                st.caption(badge.get("descripcion", ""))
    else:
        st.info("Aún no tienes insignias. Genera una hoja de estudio para ganar la primera!")

    st. divider()
    locked = [name for name in BADGE_CATALOG if name not in earned]
    if locked:
        st.subheader("🔒 Próximas Insignias")
        for name in locked:
            b = BADGE_CATALOG[name]
            st.markdown(f"- {b['emoji']} **{name}** - {b['tip']}")