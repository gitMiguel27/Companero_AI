from core.llm import get_llm
from core.prompts import STUDY_SHEET_TEMPLATE, TOPIC_EXTRACT_TEMPLATE, RAG_STUDY_SHEET_TEMPLATE
from memory.vector_store import store_chunks, retrieve_context
from core.ingestor import ingest_raw_text, ingest_uploaded_file

def generate_study_sheet(topic: str, content: str, save_to_memory: bool = True) -> str:
    """
    Generates a Spanish-language study sheet from provided content.

    If save_to_memory is True, the content chunks are stored in ChromaDB so the student can revisit this topic in a future session without re-uploading the material.

    Args:
        topic: The study subject.
        content: Raw text (already extracted from PDF or typed).
        save_to_memory: Whether to store chunks in ChromasDB.

    Returns:
        str: Formatted study sheet in Spanish (markdown).
    """
    llm = get_llm(temperature=0.3) # Low temp = factual, consistent output
    chain = STUDY_SHEET_TEMPLATE | llm
    # Truncate content if very long = LLMs have context window limits
    # 3000 chars ≈ ~600 words, safe for most models
    content_preview = content[:3000] if len(content) > 3000 else content

    result = chain.invoke({"topic": topic, "content": content_preview})

    # Store to ChromaDB in the background
    if save_to_memory:
        chunks = ingest_raw_text(content)
        store_chunks(chunks, topic=topic, source="manual")

    return result

def generate_study_sheet_from_pdf(topic: str, file_path: str) -> str:
    """
    Ingests a PDF and generates a study sheet from its content.

    Returns both the study sheet AND the extracted content so the caller can use the content for question generation without re-processing the PDF.

    Arg:
        topic: The study subject.
        file_path: Path to the uploaded PDF on disk.

    Returns:
        tuple[str, str]: (study_sheet, pdf_content)
            - study_sheet: Formatted study sheet in Spanish (markdown)
            - pdf_content: Raw extracted text used for generation
    """
    chunks = ingest_uploaded_file(file_path)

    if not chunks:
        return "⚠️ No se pudo extraer texto el PDF. Verifica que el archivo no esté protegido o sea solo imágenes."

    # Use first few chunks as the content preview for the prompt
    content_preview = "\n\n".join(chunks[:6])

    # Store all chunks in memory
    store_chunks(chunks, topic=topic, source="pdf")

    study_sheet = generate_study_sheet(topic, content_preview, save_to_memory=False)

    return study_sheet, content_preview

def generate_from_memory(topic: str) -> str:
    """
    Generates a study sheet using previously stored ChromaDB context. 
    
    This is used when the student selects a past topic from the sidebar without re-uploading material. This is the RAG flow.

    Args:
        topic: The previously studied topic to retrieve.

    Returns:
        str: Study sheet in Spanish based on retrieved memory.
    """
    context = retrieve_context(query=topic, topic=topic, k=5)

    if not context:
        return f"No se encontraron apuntes guardados sobre '{topic}'. Sube material nuevo para comenzar."

    llm = get_llm(temperature=0.3)
    chain = RAG_STUDY_SHEET_TEMPLATE | llm
    return chain.invoke({"topic": topic, "context": context})

def auto_detect_topic(content: str) -> str:
    """
    Infers a topic name from raw content using the LLM.

    Args:
        content: Raw text to analyze.

    Returns:
        str: A 3-5 word topic title in Spanish.
    """
    llm = get_llm(temperature=0.1) # Very low temp - we want a clean label
    chain = TOPIC_EXTRACT_TEMPLATE | llm
    return chain.invoke({"content": content[:1000]}).strip()