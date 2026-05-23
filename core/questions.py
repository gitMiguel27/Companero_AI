# core/study_sheet.py
from core.llm import get_llm
from core.prompts import QUESTIONS_TEMPLATE
from memory.vector_store import retrieve_context

def generate_questions(topic: str, content: str, num_questions: int = 5) -> list[dict]:
    """
    Generates Spanish-language practice questions from study content.

    Args:
        topic: The subject being studied.
        content: The source material (text).
        num_questions: How many questions to generate.

    Returns:
        list[dict]: List of {"question": str, "answer": str} dicts.
    """
    llm = get_llm(temperature=0.5)
    chain = QUESTIONS_TEMPLATE | llm
    
    content_preview = content[:3000] if len(content) > 3000 else content

    result = chain.invoke({
        "topic": topic,
        "content": content_preview,
        "num_questions": num_questions
    })

    return _parse_questions(result)

def generate_questions_from_memory(topic: str, num_questions: int = 5) -> list[dict]:
    """
    Generates questions using ChromaDB-retrieved context.

    Used when the student wants to quiz themselves on a past topic without re-uploading material.

    Args:
        topic: Previously studied topic.
        num_questions: Number of questions to generate.

    Returns:
        list[dict]: Parsed questions or empty list if no memory found.
    """
    context = retrieve_context(query=topic, topic=topic, k=4)

    if not context:
        return []

    return generate_questions(topic, context, num_questions)

def _parse_questions(raw_text: str) -> list[dict]:
    """
    Parses the LLM's raw output into structured question/answer dicts.

    Expected format from the LLM:
        P1: ¿Cuál es la función de la clorofila?
        R: La clorofila absorbe la luz solar para la fotosíntesis.

    The underscore prefix marks this as a private helper - it's only meant to be called inside this module, not imported elsewhere.

    Args:
        raw_text: Raw LLM output string.

    Returns:
        list[dict]: Parsed list of {"question": ..., "answer": ...} dicts. Skips malformed entries gracefully.
    """
    questions = []
    lines = raw_text.strip().split("\n")

    current_q = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match "P1:", "P2:", etc.
        if line.upper().startswith("P") and ":" in line and line[1:2].isdigit():
            current_q = line.split(":", 1)[1].strip()

        # Match "R:" answer lines
        elif line.upper().startswith("R:") and current_q:
            answer = line[2:].strip()
            questions.append({"question": current_q, "answer": answer})
            current_q = None

    return questions