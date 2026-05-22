# core/prompts.py
from langchain_core.prompts import PromptTemplate

# -------------------------------------------------------
# STUDY SHEET PROMPT
# Output is in Spanish by design.
# We explicitly forbid adding outside information to keep it grounded in what the student uploaded (important for test prep accuracy).
# -------------------------------------------------------
STUDY_SHEET_TEMPLATE = PromptTemplate(
    input_variables=["topic", "content"],
    template="""
Eres Compañero AI, un tutor personal amigable y alentador para estudiantes hispanohablantes.

El estudiante quiere estudiar: {topic}

Este es el material que proporcionó:
---
{content}
---

Crea una hoja de estudio concisa SOLO en español con estas secciones:

1. **Conceptos Clave** (lista de viñetas, máximo 6-8 puntos)
2. **Resumen** (3-4 oraciones de lenguaje claro y sencillo)
3. **Para Recordar** (2-3 tips memorables o reglas fáciles de recordar)

Reglas importantes:
- Responde ÚNICAMENTE en español.
- Usa solo la informatció del material proporcionado.
- El tono debe ser alentador y accesible para estudiantes de prepatoria.
- No agregues información que no esté en el material.
"""
)

# -------------------------------------------------------
# PRACTICE QUESTIONS PROMPT
# Strict format is critical — our parser depends on it.
# Specifying "R1:", "A:" makes the response machine-readable.
# -------------------------------------------------------
QUESTIONS_TEMPLATE = PromptTemplate(
    input_variables=["topic", "content", "num_questions"],
    template="""
Eres Compañero AI, un tutor que crea exámenes de práctica en español.

Tema: {topic}

Material de estudio:
---
{content}
---

Genera exactamente {num_qestions} preguantas de práctica BASADAS SOLO en el material anterior.

Formato obligatorio (respeta exactemente este formato):
P1: [texto de la pregunta]
R: [respuesta correcta]

P2: [texto de la pregunta]
R: [respuesta correcta]

Incluye una mezcla de pregunatas de opción múltiple y respuesta corta. Todas las preguntas y respuestas deben estar en español.
"""
)

# -------------------------------------------------------
# TOPIC EXTRACTION PROMPT
# Used when the student doesn't type a topic - we infer it from their content.
# Very short output — used as a label in the UI and ChromaDB.
# -------------------------------------------------------
TOPIC_EXTRACT_TEMPLATE = PromptTemplate(
    input_variables=["content"],
    template="""
Lee el siguiente texto y responde SOLO con un título de tema de 3-5 palabras en español.
Nada más - solo el título.

Texto:
{content}
"""
)

# -------------------------------------------------------
# RAG STUDY SHEET PROMPT
# Used when pulling context from ChromaDB memory (context-aware).
# -------------------------------------------------------
RAG_STUDY_SHEET_TEMPLATE = PromptTemplate(
    input_variables=["topic", "context"],
    template="""
Eres Compañero AI. Basándote en los apuntes previos del estudiante sobre "{topic}", crea una hoja de estudio actualizada en español.

Apuntes recuperados:
---
{context}
---
Crea la hoja de estudio con:
1. **Conceptos Clave** (viñetas, máximo 8)
2. **Resumen** (3-4 oraciones)
3. **Para Recordar** (2-3 tips clave)

Responsde ÚNICAMENTE en español.
"""
)