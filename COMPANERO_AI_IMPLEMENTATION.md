# Compañero AI — Implementation Plan
## CAP 942 · AI-Driven Personal Tutor for Spanish-Speaking Students

> **How to use this guide:** Each phase builds directly on the last. Work through one step at a time — read the code, understand it, then type it yourself. Annotations explain *why* each decision was made, not just *what* to do. This is how you build real Software Engineering intuition.

---

## Table of Contents

1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Project Structure](#2-project-structure)
3. [Phase 1 — Environment Setup](#3-phase-1--environment-setup)
4. [Phase 2 — PDF Ingestion with pdfplumber](#4-phase-2--pdf-ingestion-with-pdfplumber)
5. [Phase 3 — LLM Integration (Ollama + Llama 3.2)](#5-phase-3--llm-integration-ollama--llama-32)
6. [Phase 4 — ChromaDB Memory Layer](#6-phase-4--chromadb-memory-layer)
7. [Phase 5 — Core Chains (Study Sheet + Questions)](#7-phase-5--core-chains-study-sheet--questions)
8. [Phase 6 — Streamlit UI](#8-phase-6--streamlit-ui)
9. [Phase 7 — Rewards & Milestone System](#9-phase-7--rewards--milestone-system)
10. [Phase 8 — Polish & Documentation](#10-phase-8--polish--documentation)
11. [Future Feature Branch: TTS/STT](#11-future-feature-branch-ttsstt)
12. [Submission Checklist](#12-submission-checklist)

---

## 1. Project Overview & Architecture

**App Name:** Compañero AI  
**Core Problem:** Spanish-speaking students learn content in English but test in Spanish (e.g. NYS Regents). They face both a learning barrier and a language barrier simultaneously.  
**Solution:** An AI tutor that accepts uploaded PDFs or typed notes and generates Spanish-language study sheets, practice questions, and remembers past sessions.

### What makes this project unique vs. a generic chatbot

| Generic Chatbot | Compañero AI |
|---|---|
| Stateless — forgets everything | ChromaDB stores notes between sessions |
| English only | Output generated in Spanish by default |
| Text input only | Accepts PDF uploads via pdfplumber |
| No study structure | Structured study sheets + formatted quizzes |

### System Architecture (Data Flow)

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI                        │
│   [Upload PDF]  [Type Notes]  [Topic Input]          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              Ingestion Layer                         │
│   pdfplumber extracts text  →  text chunker         │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐   ┌──────────────────────────────┐
│   ChromaDB       │   │      LangChain Chains         │
│  (vector store)  │   │  StudySheetChain              │
│  stores chunks   │   │  QuestionChain                │
│  & embeddings    │   │  (prompts in Spanish)         │
└──────────────────┘   └────────────┬─────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │   Ollama — Llama 3.2        │
                        │   (local, no API key)       │
                        └────────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │   Streamlit Output          │
                        │   Study Sheet (ES)          │
                        │   Practice Quiz (ES)        │
                        │   Rewards / Badges          │
                        └────────────────────────────┘
```

---

## 2. Project Structure

Plan your structure before writing code. This is a Software Engineering discipline — it forces you to think in layers before you think in lines.

```
companero-ai/
├── app.py                    # Streamlit entry point
├── pyproject.toml            # uv dependency config
├── .env                      # environment variables (never commit)
├── .gitignore
├── README.md
│
├── core/
│   ├── __init__.py
│   ├── llm.py                # Ollama + LangChain LLM setup
│   ├── prompts.py            # All Spanish-language prompt templates
│   ├── study_sheet.py        # Study sheet generation chain
│   ├── questions.py          # Practice question generation chain
│   └── ingestor.py           # PDF + text extraction with pdfplumber
│
├── memory/
│   ├── __init__.py
│   ├── vector_store.py       # ChromaDB setup and operations
│   └── embeddings.py         # Embedding model config
│
├── state/
│   ├── __init__.py
│   └── session.py            # Streamlit session state + milestones
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py            # Upload, topic input, settings
│   ├── study_view.py         # Study sheet display tab
│   ├── quiz_view.py          # Practice questions tab
│   └── rewards_view.py       # Badges and progress tab
│
└── uploads/                  # Temp folder for uploaded PDFs
    └── .gitkeep              # Keeps folder in git without content
```

> **Why separate `core/`, `memory/`, `state/`, and `ui/?`** Each folder has one job. `core/` handles AI logic. `memory/` handles persistence. `state/` handles the UI's runtime data. `ui/` handles display. If ChromaDB needs to change to a different vector DB later, you only touch the `memory/` folder — nothing else breaks.

---

## 3. Phase 1 — Environment Setup

### Step 1.1 — Clone your repo and initialize the project

Open your Codespaces terminal:

```bash
# You should already be in your Compa-ero_AI repo
# Verify:
git remote -v
# Should show: origin https://github.com/gitMiguel27/Compa-ero_AI.git

# Create your project folders
mkdir -p core memory state ui uploads
touch core/__init__.py memory/__init__.py state/__init__.py ui/__init__.py
touch uploads/.gitkeep

# Initialize uv
uv init
uv venv
source .venv/bin/activate
```

---

### Step 1.2 — Install all dependencies

```bash
uv add streamlit \
       langchain \
       langchain-community \
       langchain-chroma \
       chromadb \
       pdfplumber \
       sentence-transformers \
       ollama \
       python-dotenv
```

> **What each package does:**
> - `langchain` + `langchain-community` — LLM chain orchestration
> - `langchain-chroma` — Official LangChain ↔ ChromaDB bridge
> - `chromadb` — Local vector database (stores + searches text embeddings)
> - `pdfplumber` — Accurate PDF text extraction (better than PyPDF2 for Spanish characters)
> - `sentence-transformers` — Creates text embeddings for ChromaDB (runs locally, no API)
> - `python-dotenv` — Loads `.env` config variables

---

### Step 1.3 — Install Ollama and pull Llama 3.2

```bash
# Install Ollama (Linux/Codespaces)
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 — better multilingual + Spanish support than Llama 3
ollama pull llama3.2

# Start Ollama server in the background
ollama serve &

# Quick sanity check
ollama run llama3.2 "Di hola en español en una sola oración."
```

> **Why Llama 3.2 over Llama 3?** Llama 3.2 has improved multilingual benchmarks, especially for Spanish. For a Spanish-first app, this matters. The 3B model runs comfortably on Codespaces CPU; use 1B if you experience slowness.

---

### Step 1.4 — Create your .env and .gitignore

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

```bash
# .gitignore
.venv/
__pycache__/
*.pyc
.env
.DS_Store
chroma_db/
uploads/*.pdf
```

> **Why ignore `chroma_db/`?** ChromaDB creates a local folder of binary files. These are large, machine-specific, and shouldn't be in version control. Each developer (or Codespace) builds their own local database.

---

### Step 1.5 — Commit your scaffold

```bash
git checkout -b feat/project-scaffold
git add .
git commit -m "chore: initialize project structure, dependencies, and env config"
git push -u origin feat/project-scaffold
```

Then open a PR on GitHub → merge → `git checkout main && git pull origin main`.

---

## 4. Phase 2 — PDF Ingestion with pdfplumber

### Step 2.1 — Understand the ingestion problem

Before writing code, think through the problem:

1. A student uploads a PDF (e.g. a textbook chapter in English)
2. We need to extract the raw text
3. We need to break it into manageable **chunks** (ChromaDB can't store an entire textbook as one blob)
4. Those chunks get stored in ChromaDB with embeddings (vector representations) so we can search them later

This process is called **document ingestion** — it's the foundation of any RAG (Retrieval-Augmented Generation) app.

---

### Step 2.2 — Create the ingestor module

Create `core/ingestor.py`:

```python
# core/ingestor.py
import pdfplumber
from pathlib import Path


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file using pdfplumber.

    pdfplumber handles Spanish characters (accents, ñ, etc.) correctly,
    which is why we chose it over PyPDF2 for this project.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        str: All extracted text concatenated, page by page.
             Returns empty string if extraction fails.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # Some pages are images — skip if None
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text.strip()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits a long text into overlapping chunks for ChromaDB storage.

    Why overlap? If a key concept spans two chunks, overlap ensures it's
    captured in at least one chunk's context window. Without overlap,
    you'd lose information at chunk boundaries.

    Args:
        text:       The full text to split.
        chunk_size: Target character count per chunk (500 ≈ ~100 words).
        overlap:    How many characters to repeat between consecutive chunks.

    Returns:
        list[str]: List of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():  # Skip chunks that are only whitespace
            chunks.append(chunk.strip())
        start += chunk_size - overlap  # Step forward, minus the overlap

    return chunks


def ingest_uploaded_file(file_path: str) -> list[str]:
    """
    Full pipeline: PDF file → extracted text → chunks.

    This is the function the rest of the app calls.
    It abstracts away whether the source is a PDF or plain text.

    Args:
        file_path: Path to the uploaded file.

    Returns:
        list[str]: Text chunks ready for ChromaDB storage.
    """
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        # Fallback: treat as plain text file
        text = path.read_text(encoding="utf-8", errors="ignore")

    return chunk_text(text)


def ingest_raw_text(text: str) -> list[str]:
    """
    Pipeline for text typed directly into the UI (not a file upload).

    Args:
        text: Raw string from the Streamlit text area.

    Returns:
        list[str]: Text chunks ready for ChromaDB storage.
    """
    return chunk_text(text)
```

---

### Step 2.3 — Test your ingestor

Create a quick test script (delete after confirming it works):

```python
# test_ingestor.py
from core.ingestor import extract_text_from_pdf, chunk_text, ingest_raw_text

# Test chunking with raw text
sample = """
La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar
en energía química. Este proceso ocurre principalmente en los cloroplastos, 
donde la clorofila absorbe la luz. Los productos finales son glucosa y oxígeno.
La glucosa es utilizada como fuente de energía por la planta, mientras que el 
oxígeno es liberado a la atmósfera como subproducto.
""" * 5  # Repeat to create a longer text

chunks = ingest_raw_text(sample)
print(f"Total chunks: {len(chunks)}")
print(f"First chunk preview:\n{chunks[0][:200]}")
print(f"Overlap check — end of chunk 0: ...{chunks[0][-50:]}")
print(f"Start of chunk 1: {chunks[1][:50]}...")
```

Run it:

```bash
python test_ingestor.py
```

> **Checkpoint:** You should see 3–5 chunks with visible overlap between consecutive ones. If you see only 1 chunk, your sample text is too short — the repeat count handles this.

---

## 5. Phase 3 — LLM Integration (Ollama + Llama 3.2)

### Step 3.1 — Create the LLM module

Create `core/llm.py`:

```python
# core/llm.py
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

load_dotenv()


def get_llm(temperature: float = 0.5) -> OllamaLLM:
    """
    Returns a configured Ollama LLM instance pointed at Llama 3.2.

    Temperature guide for this project:
      0.2–0.4 → factual study sheets (we want accuracy, not creativity)
      0.5–0.6 → practice questions (some variety is good)
      0.7+    → conversational tone (future stretch goal)

    Args:
        temperature: Creativity dial (0.0 = deterministic, 1.0 = very creative)

    Returns:
        OllamaLLM: A LangChain-compatible LLM ready to call.
    """
    return OllamaLLM(
        model=os.getenv("MODEL_NAME", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
    )
```

---

### Step 3.2 — Create Spanish-language prompt templates

This is the most important file in the project. Well-crafted prompts are the difference between a useful study sheet and a generic one. Create `core/prompts.py`:

```python
# core/prompts.py
from langchain_core.prompts import PromptTemplate

# ─────────────────────────────────────────────────────────────────────────────
# STUDY SHEET PROMPT
# Output is in Spanish by design — this is the core language requirement.
# We explicitly forbid adding outside information to keep it grounded
# in what the student uploaded (important for test prep accuracy).
# ─────────────────────────────────────────────────────────────────────────────
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

1. **Conceptos Clave** (lista de viñetas, máximo 6–8 puntos)
2. **Resumen** (3–4 oraciones en lenguaje claro y sencillo)
3. **Para Recordar** (2–3 tips memorables o reglas fáciles de recordar)

Reglas importantes:
- Responde ÚNICAMENTE en español.
- Usa solo la información del material proporcionado.
- El tono debe ser alentador y accesible para estudiantes de preparatoria.
- No agregues información que no esté en el material.
"""
)

# ─────────────────────────────────────────────────────────────────────────────
# PRACTICE QUESTIONS PROMPT
# Strict output format is critical here — our parser depends on it.
# Specifying "Q1:", "A:" makes the response machine-readable.
# ─────────────────────────────────────────────────────────────────────────────
QUESTIONS_TEMPLATE = PromptTemplate(
    input_variables=["topic", "content", "num_questions"],
    template="""
Eres Compañero AI, un tutor que crea exámenes de práctica en español.

Tema: {topic}

Material de estudio:
---
{content}
---

Genera exactamente {num_questions} preguntas de práctica BASADAS SOLO en el material anterior.

Formato obligatorio (respeta exactamente este formato):
P1: [texto de la pregunta]
R: [respuesta correcta]

P2: [texto de la pregunta]
R: [respuesta correcta]

Incluye una mezcla de preguntas de opción múltiple y respuesta corta.
Todas las preguntas y respuestas deben estar en español.
"""
)

# ─────────────────────────────────────────────────────────────────────────────
# TOPIC EXTRACTION PROMPT
# Used when the student doesn't type a topic — we infer it from their content.
# Very short output (3–5 words) to use as a label in the UI and ChromaDB.
# ─────────────────────────────────────────────────────────────────────────────
TOPIC_EXTRACT_TEMPLATE = PromptTemplate(
    input_variables=["content"],
    template="""
Lee el siguiente texto y responde SOLO con un título de tema de 3–5 palabras en español.
Nada más — solo el título.

Texto:
{content}
"""
)

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT-AWARE STUDY SHEET (uses ChromaDB retrieved chunks)
# Used when the student asks about a past topic — we pull stored context.
# ─────────────────────────────────────────────────────────────────────────────
RAG_STUDY_SHEET_TEMPLATE = PromptTemplate(
    input_variables=["topic", "context"],
    template="""
Eres Compañero AI. Basándote en los apuntes previos del estudiante sobre "{topic}",
crea una hoja de estudio actualizada en español.

Apuntes recuperados:
---
{context}
---

Crea la hoja de estudio con:
1. **Conceptos Clave** (viñetas, máximo 8)
2. **Resumen** (3–4 oraciones)
3. **Para Recordar** (2–3 tips clave)

Responde ÚNICAMENTE en español.
"""
)
```

> **Prompt Engineering insight:** Notice how every prompt ends with a rule like "Responde ÚNICAMENTE en español." LLMs can drift back to English, especially Llama models. Repeating the language requirement at the end of the prompt reinforces it near the model's attention window.

---

### Step 3.3 — Test your LLM connection

```python
# test_llm.py (delete after testing)
from core.llm import get_llm

llm = get_llm(temperature=0.3)
response = llm.invoke(
    "¿Qué es la fotosíntesis? Explica en 2 oraciones en español."
)
print(response)
```

```bash
python test_llm.py
```

> **Checkpoint:** You should receive a Spanish-language 2-sentence explanation. If you get English, the model is available but not following the prompt — double-check you pulled `llama3.2` and not `llama3`.

---

## 6. Phase 4 — ChromaDB Memory Layer

### Step 4.1 — Understand what ChromaDB does here

ChromaDB is a **vector database**. Here's the mental model:

- Text gets converted to **embeddings** (arrays of numbers that represent meaning)
- ChromaDB stores those embeddings with the original text
- When a student asks about a topic, we convert their query to an embedding and find the stored chunks that are **mathematically closest** to it
- Those closest chunks become the **context** we feed to the LLM

This is what "memory" means for Compañero AI — not memory like RAM, but semantic memory: *"I've seen notes about fotosíntesis before, here's what was in them."*

---

### Step 4.2 — Create the embeddings config

Create `memory/embeddings.py`:

```python
# memory/embeddings.py
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    """
    Returns a sentence-transformer embedding model.

    We use 'all-MiniLM-L6-v2' because:
    - It's small (~80MB), fast, and runs on CPU
    - It supports multilingual text including Spanish
    - It's the most common embedding model for local RAG apps

    This model downloads once on first use (~80MB).
    Subsequent uses load from local cache.

    Returns:
        HuggingFaceEmbeddings: An embedding function compatible
        with LangChain and ChromaDB.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

---

### Step 4.3 — Create the vector store module

Create `memory/vector_store.py`:

```python
# memory/vector_store.py
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from memory.embeddings import get_embeddings

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def get_vector_store(collection_name: str = "companero_notes") -> Chroma:
    """
    Returns a ChromaDB vector store instance.

    The collection_name acts like a table name — it groups related documents.
    Using one collection per app keeps things simple for the MVP.
    You could extend this to one collection per student in the future.

    Args:
        collection_name: Name of the ChromaDB collection to use/create.

    Returns:
        Chroma: A LangChain-compatible vector store object.
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def store_chunks(chunks: list[str], topic: str, source: str = "upload") -> int:
    """
    Stores text chunks in ChromaDB with metadata tags.

    Metadata is key — it lets us filter by topic later so the student's
    notes on "Fotosíntesis" don't bleed into their "Guerra Civil" notes.

    Args:
        chunks:  List of text chunks from the ingestor.
        topic:   The study topic (used as a metadata filter later).
        source:  Where the content came from ('upload' or 'typed').

    Returns:
        int: Number of chunks successfully stored.
    """
    if not chunks:
        return 0

    store = get_vector_store()

    # Wrap each chunk as a LangChain Document with metadata
    documents = [
        Document(
            page_content=chunk,
            metadata={"topic": topic.lower(), "source": source}
        )
        for chunk in chunks
    ]

    store.add_documents(documents)
    return len(documents)


def retrieve_context(query: str, topic: str = None, k: int = 4) -> str:
    """
    Retrieves the most relevant stored chunks for a given query.

    This is the "retrieval" in RAG. We search ChromaDB for the k chunks
    most semantically similar to the query and return them as a single
    context string to feed into our LLM prompt.

    Args:
        query:  The search query (usually the topic or a question).
        topic:  Optional filter — only search within a specific topic.
        k:      Number of chunks to retrieve (4 is a good default).

    Returns:
        str: Retrieved chunks joined into a single context block.
             Returns empty string if nothing is found.
    """
    store = get_vector_store()

    # Build optional metadata filter
    filter_dict = {"topic": topic.lower()} if topic else None

    try:
        results = store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        if not results:
            return ""

        # Join chunks with a separator for readability in the prompt
        return "\n\n---\n\n".join([doc.page_content for doc in results])

    except Exception as e:
        print(f"ChromaDB retrieval error: {e}")
        return ""


def get_stored_topics() -> list[str]:
    """
    Returns a list of unique topics stored in ChromaDB.

    Used in the UI sidebar to let students pick a past topic
    instead of re-uploading material.

    Returns:
        list[str]: Sorted list of unique topic names.
    """
    store = get_vector_store()
    try:
        # ChromaDB's .get() returns all stored documents with metadata
        result = store.get()
        topics = set()
        for meta in result.get("metadatas", []):
            if meta and "topic" in meta:
                topics.add(meta["topic"])
        return sorted(list(topics))
    except Exception:
        return []
```

---

### Step 4.4 — Test ChromaDB

```python
# test_chroma.py (delete after testing)
from core.ingestor import ingest_raw_text
from memory.vector_store import store_chunks, retrieve_context, get_stored_topics

# Store some test content
sample = """
La mitosis es el proceso de división celular en el que una célula madre 
se divide para producir dos células hijas idénticas. Ocurre en cuatro 
fases: profase, metafase, anafase y telofase. Es fundamental para el 
crecimiento y la reparación de tejidos en organismos eucariotas.
"""

chunks = ingest_raw_text(sample)
stored = store_chunks(chunks, topic="Mitosis")
print(f"Stored {stored} chunks")

# Retrieve
context = retrieve_context("¿Cuáles son las fases de la mitosis?", topic="mitosis")
print(f"\nRetrieved context:\n{context[:300]}...")

# List topics
print(f"\nStored topics: {get_stored_topics()}")
```

```bash
python test_chroma.py
```

> **Checkpoint:** You should see chunks stored, a retrieved context block that mentions the phases, and `['mitosis']` in the topics list. A `chroma_db/` folder will appear in your project root — that's normal.

---

## 7. Phase 5 — Core Chains (Study Sheet + Questions)

### Step 5.1 — Build the study sheet generator

Create `core/study_sheet.py`:

```python
# core/study_sheet.py
from core.llm import get_llm
from core.prompts import STUDY_SHEET_TEMPLATE, TOPIC_EXTRACT_TEMPLATE, RAG_STUDY_SHEET_TEMPLATE
from memory.vector_store import store_chunks, retrieve_context
from core.ingestor import ingest_raw_text, ingest_uploaded_file


def generate_study_sheet(topic: str, content: str, save_to_memory: bool = True) -> str:
    """
    Generates a Spanish-language study sheet from provided content.

    If save_to_memory is True, the content chunks are stored in ChromaDB
    so the student can revisit this topic in a future session without
    re-uploading the material.

    Args:
        topic:          The study subject.
        content:        Raw text (already extracted from PDF or typed).
        save_to_memory: Whether to store chunks in ChromaDB.

    Returns:
        str: Formatted study sheet in Spanish (markdown).
    """
    llm = get_llm(temperature=0.3)  # Low temp = factual, consistent output
    chain = STUDY_SHEET_TEMPLATE | llm

    # Truncate content if very long — LLMs have context window limits
    # 3000 chars ≈ ~600 words, safe for most models
    content_preview = content[:3000] if len(content) > 3000 else content

    result = chain.invoke({"topic": topic, "content": content_preview})

    # Store to ChromaDB in the background
    if save_to_memory:
        chunks = ingest_raw_text(content)
        store_chunks(chunks, topic=topic, source="manual")

    return result["text"]


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

    This is used when the student selects a past topic from the sidebar
    without re-uploading material. This is the RAG flow.

    Args:
        topic: The previously studied topic to retrieve.

    Returns:
        str: Study sheet in Spanish based on retrieved memory.
    """
    context = retrieve_context(query=topic, topic=topic, k=5)

    if not context:
        return f"⚠️ No se encontraron apuntes guardados sobre '{topic}'. Sube material nuevo para comenzar."

    llm = get_llm(temperature=0.3)
    chain = RAG_STUDY_SHEET_TEMPLATE | llm
    return chain.invoke({"topic": topic, "context": context})


def auto_detect_topic(content: str) -> str:
    """
    Infers a topic name from raw content using the LLM.

    Args:
        content: Raw text to analyze.

    Returns:
        str: A 3–5 word topic title in Spanish.
    """
    llm = get_llm(temperature=0.1)  # Very low temp — we want a clean label
    chain = TOPIC_EXTRACT_TEMPLATE | llm
    return chain.invoke({"content": content[:1000]}).strip()
```

---

### Step 5.2 — Build the question generator

Create `core/questions.py`:

```python
# core/questions.py
from core.llm import get_llm
from core.prompts import QUESTIONS_TEMPLATE
from memory.vector_store import retrieve_context


def generate_questions(topic: str, content: str, num_questions: int = 5) -> list[dict]:
    """
    Generates Spanish-language practice questions from study content.

    Args:
        topic:         The subject being studied.
        content:       The source material (text).
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

    return _parse_questions(result["text"])


def generate_questions_from_memory(topic: str, num_questions: int = 5) -> list[dict]:
    """
    Generates questions using ChromaDB-retrieved context.

    Used when the student wants to quiz themselves on a past topic
    without re-uploading material.

    Args:
        topic:         Previously studied topic.
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

    We use "P" (Pregunta) and "R" (Respuesta) to match our Spanish prompt.

    Args:
        raw_text: Raw LLM output string.

    Returns:
        list[dict]: Parsed list of {"question": ..., "answer": ...} dicts.
                    Skips malformed entries gracefully.
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
```

> **Edge case handled:** The parser checks `line[1:2].isdigit()` to ensure we only match actual question lines like "P1:" and not random words starting with P. Defensive parsing like this prevents the UI from breaking when the LLM occasionally drifts from the format.

---

## 8. Phase 6 — Streamlit UI

### Step 8.1 — Session state and milestone tracking

Create `state/session.py`:

```python
# state/session.py
import streamlit as st


def init_session_state():
    """
    Initializes all session state variables used across the app.

    Streamlit re-runs the entire script on every user interaction.
    Session state is how we persist data (like a generated study sheet)
    between those re-runs without losing it.

    Call this at the very top of app.py before any rendering.
    """
    defaults = {
        "topic": "",
        "raw_content": "",
        "study_sheet": None,
        "questions": [],
        "revealed_answers": set(),
        "input_mode": "text",       # "text" or "pdf"
        "use_memory": False,        # True if loading from past session
        "milestones": {
            "study_sheets_generated": 0,
            "questions_answered":     0,
            "sessions_completed":     0,
            "pdfs_uploaded":          0,
        },
        "badges_earned": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_and_award_badges():
    """
    Evaluates current milestone counts and awards new badges.
    Displays a toast notification for each newly earned badge.

    Add new rules to the `rules` list to add new badge types.
    """
    m = st.session_state.milestones
    earned = st.session_state.badges_earned

    rules = [
        (m["study_sheets_generated"] >= 1,  "Primera Hoja de Estudio", "📄"),
        (m["study_sheets_generated"] >= 5,  "Máquina de Estudio",      "🚀"),
        (m["questions_answered"]     >= 5,  "Primer Examen",           "🎯"),
        (m["questions_answered"]     >= 20, "Campeón de Exámenes",     "🏆"),
        (m["sessions_completed"]     >= 3,  "Estudiante Constante",    "🔥"),
        (m["pdfs_uploaded"]          >= 1,  "Primer PDF",              "📚"),
    ]

    for condition, badge_name, emoji in rules:
        if condition and badge_name not in earned:
            earned.append(badge_name)
            st.toast(f"{emoji} ¡Insignia desbloqueada: **{badge_name}**!", icon=emoji)
```

---

### Step 8.2 — Build the main app entry point

Create `app.py`:

```python
# app.py
import streamlit as st
from state.session import init_session_state
from ui.sidebar import render_sidebar
from ui.study_view import render_study_view
from ui.quiz_view import render_quiz_view
from ui.rewards_view import render_rewards_view

# ── Page config — MUST be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="Compañero AI",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize all session state ─────────────────────────────────────────────
init_session_state()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧑‍🏫 Compañero AI")
st.caption(
    "Tu tutor personal con IA. Sube tus apuntes o un PDF "
    "y obtén una hoja de estudio y preguntas de práctica en español."
)
st.divider()

# ── Sidebar (inputs and controls) ─────────────────────────────────────────────
render_sidebar()

# ── Main content area ─────────────────────────────────────────────────────────
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
    # ── Empty state shown before first generation ──────────────────────────
    st.info(
        "👈 Ingresa tu tema y material en la barra lateral, "
        "luego haz clic en **Generar Hoja de Estudio** para comenzar."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Hojas Generadas", "—")
    col2.metric("❓ Preguntas Respondidas", "—")
    col3.metric("🏆 Insignias", "—")
```

---

### Step 8.3 — Build the sidebar

Create `ui/sidebar.py`:

```python
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

        # ── Topic input ────────────────────────────────────────────────────
        topic = st.text_input(
            "Tema",
            placeholder="ej. Fotosíntesis, La Revolución Mexicana, Ecuaciones Cuadráticas",
            key="topic_input"
        )

        st.divider()

        # ── Input mode selector ────────────────────────────────────────────
        input_mode = st.radio(
            "¿Cómo quieres ingresar tu material?",
            options=["Escribir / Pegar texto", "Subir PDF", "Usar tema guardado"],
            key="input_mode_radio"
        )

        content = ""
        file_path = None

        # ── Mode: type/paste text ──────────────────────────────────────────
        if input_mode == "Escribir / Pegar texto":
            content = st.text_area(
                "Pega tus apuntes aquí",
                placeholder="Pega el texto de tu libro, tus notas de clase o cualquier material...",
                height=220,
                key="content_input"
            )

        # ── Mode: upload PDF ───────────────────────────────────────────────
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

        # ── Mode: use past memory ──────────────────────────────────────────
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

        # ── Number of questions ────────────────────────────────────────────
        st.divider()
        num_questions = st.slider(
            "Número de preguntas de práctica",
            min_value=3, max_value=10, value=5,
            key="num_questions"
        )

        # ── Auto-detect topic button ───────────────────────────────────────
        if content and not topic:
            if st.button("🔍 Detectar tema automáticamente", use_container_width=True):
                with st.spinner("Detectando tema..."):
                    detected = auto_detect_topic(content)
                    st.session_state.topic = detected
                    st.rerun()

        # ── Main generate button ───────────────────────────────────────────
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
    """Orchestrates study sheet + question generation based on input mode."""
    use_memory = st.session_state.get("use_memory", False)

    with st.spinner("📖 Generando tu hoja de estudio en español..."):
        if use_memory:
            study_sheet = generate_from_memory(topic)
            questions   = generate_questions_from_memory(topic, num_questions)
            st.session_state.use_memory = False

        elif file_path:
            study_sheet, pdf_content = generate_study_sheet_from_pdf(topic, file_path)
            questions   = generate_questions(topic, content or "", num_questions)
            st.session_state.milestones["pdfs_uploaded"] += 1

        else:
            study_sheet = generate_study_sheet(topic, content)
            questions   = generate_questions(topic, content, num_questions)

    st.session_state.study_sheet = study_sheet
    st.session_state.questions   = questions
    st.session_state.topic       = topic
    st.session_state.raw_content = content
    st.session_state.revealed_answers = set()
    st.session_state.milestones["study_sheets_generated"] += 1

    check_and_award_badges()
    st.success("✅ ¡Listo! Revisa las pestañas arriba.")
```

---

### Step 8.4 — Build the study sheet view

Create `ui/study_view.py`:

```python
# ui/study_view.py
import streamlit as st


def render_study_view():
    if not st.session_state.study_sheet:
        st.info("Aún no hay hoja de estudio. ¡Genera una desde la barra lateral!")
        return

    st.subheader(f"📄 Hoja de Estudio: {st.session_state.topic}")
    st.markdown(st.session_state.study_sheet)
    st.divider()

    # Download button — students can save and print their study sheets
    st.download_button(
        label="⬇️ Descargar Hoja de Estudio",
        data=st.session_state.study_sheet,
        file_name=f"hoja_estudio_{st.session_state.topic.replace(' ', '_')}.md",
        mime="text/markdown",
    )
```

---

### Step 8.5 — Build the quiz view

Create `ui/quiz_view.py`:

```python
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
                st.success(f"✅ **Respuesta:** {q['answer']}")
            else:
                st.caption("Piénsalo primero, luego haz clic para revelar.")
                if st.button(f"Revelar Respuesta", key=f"reveal_{i}"):
                    st.session_state.revealed_answers.add(i)
                    st.session_state.milestones["questions_answered"] += 1
                    check_and_award_badges()
                    st.rerun()

    # Progress bar
    answered = len(st.session_state.revealed_answers)
    total    = len(questions)
    st.divider()
    st.progress(answered / total if total > 0 else 0)
    st.caption(f"Reveladas {answered} de {total} respuestas")

    if answered == total and total > 0:
        st.balloons()
        st.success("🎉 ¡Repasaste todas las preguntas! ¡Excelente trabajo!")
        st.session_state.milestones["sessions_completed"] += 1
        check_and_award_badges()
```

---

### Step 8.6 — Build the rewards view

Create `ui/rewards_view.py`:

```python
# ui/rewards_view.py
import streamlit as st

BADGE_CATALOG = {
    "Primera Hoja de Estudio": {
        "emoji": "📄",
        "descripcion": "Generaste tu primera hoja de estudio.",
        "tip": "¡Sigue adelante — genera 5 para desbloquear Máquina de Estudio!"
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
        "tip": "¡Sigue — 20 respuestas te dan el Campeón de Exámenes!"
    },
    "Campeón de Exámenes": {
        "emoji": "🏆",
        "descripcion": "Revelaste 20 respuestas.",
        "tip": "¡Dedicación extraordinaria!"
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
    col1.metric("📄 Hojas Generadas",     m["study_sheets_generated"])
    col2.metric("❓ Preguntas Respondidas", m["questions_answered"])
    col3.metric("✅ Sesiones Completadas",  m["sessions_completed"])
    col4.metric("📚 PDFs Subidos",          m["pdfs_uploaded"])

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
        st.info("Aún no tienes insignias. ¡Genera una hoja de estudio para ganar la primera!")

    st.divider()
    locked = [name for name in BADGE_CATALOG if name not in earned]
    if locked:
        st.subheader("🔒 Próximas Insignias")
        for name in locked:
            b = BADGE_CATALOG[name]
            st.markdown(f"- {b['emoji']} **{name}** — {b['tip']}")
```

---

### Step 8.7 — Run the full app

```bash
# Make sure Ollama is running
ollama serve &

# Launch
streamlit run app.py
```

In Codespaces the app will be at `http://localhost:8501`. Check the **Ports** tab in VS Code if it doesn't auto-forward.

---

## 9. Phase 7 — Rewards & Milestone System

The rewards system is already wired in. Run through this manual test checklist:

| Action | Expected Result |
|---|---|
| Generate first study sheet | Toast: "📄 ¡Insignia desbloqueada: Primera Hoja de Estudio!" |
| Upload a PDF | Toast: "📚 ¡Insignia desbloqueada: Primer PDF!" |
| Reveal 5 quiz answers | Toast: "🎯 ¡Insignia desbloqueada: Primer Examen!" |
| Reveal all answers in a session | Balloons + "Sesiones Completadas" counter increments |
| Reveal 20 total answers | Toast: "🏆 Campeón de Exámenes" |
| Logros tab | Earned badges show, locked ones listed with tip |

---

## 10. Phase 8 — Polish & Documentation

### Step 10.1 — Add missing `__init__.py` files

```bash
touch core/__init__.py memory/__init__.py state/__init__.py ui/__init__.py
```

### Step 10.2 — Final project structure verification

```bash
find . -type f -name "*.py" | sort
```

Expected output:
```
./app.py
./core/__init__.py
./core/ingestor.py
./core/llm.py
./core/prompts.py
./core/questions.py
./core/study_sheet.py
./memory/__init__.py
./memory/embeddings.py
./memory/vector_store.py
./state/__init__.py
./state/session.py
./ui/__init__.py
./ui/quiz_view.py
./ui/rewards_view.py
./ui/sidebar.py
./ui/study_view.py
```

### Step 10.3 — Update README.md

```markdown
# Compañero AI 🧑‍🏫
**AI-Driven Personal Tutor for Spanish-Speaking Students**

## Problem Statement
Spanish-speaking students often learn content in English but are tested in Spanish 
(e.g. NYS Regents). Compañero AI bridges this gap by generating study sheets and 
practice questions in Spanish from any uploaded material.

## Features
- Upload a PDF or paste notes → instant Spanish study sheet
- AI-generated practice quiz with reveal mechanic
- ChromaDB memory — revisit past topics without re-uploading
- Milestone badge rewards system
- All output in Spanish by default

## Tech Stack
| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Ollama + Llama 3.2 | Local LLM (multilingual) |
| LangChain | Prompt chain orchestration |
| pdfplumber | PDF text extraction |
| ChromaDB | Vector database for session memory |
| Sentence-Transformers | Local text embeddings |
| Streamlit | UI |
| uv | Package management |

## Setup

### Prerequisites
- Python 3.11+, uv installed, Ollama installed

\`\`\`bash
git clone https://github.com/gitMiguel27/Compa-ero_AI
cd Compa-ero_AI
uv venv && source .venv/bin/activate
uv add streamlit langchain langchain-community langchain-chroma \
    chromadb pdfplumber sentence-transformers ollama python-dotenv
ollama pull llama3.2
ollama serve &
streamlit run app.py
\`\`\`

## Workflow Diagram
[Add diagram image here]
```

### Step 10.4 — Final commit to main

```bash
git add .
git commit -m "feat: complete Compañero AI MVP with PDF, ChromaDB, Spanish output"
git push origin main
```

---

## 11. Future Feature Branch: TTS/STT

When you're ready to add voice features, branch off main:

```bash
git checkout -b feat/voice-io
```

Packages to add:
```bash
uv add openai-whisper pyttsx3
```

Planned new files:
- `core/tts.py` — `speak_spanish(text: str)` with `pyttsx3` (set `lang='es'`)
- `core/stt.py` — `transcribe_audio(file_path: str)` using Whisper `base` model
- `ui/voice_controls.py` — Streamlit `st.audio_input()` widget (v1.31+)

> **Note:** Voice I/O requires microphone access — test locally on your Intel Mac, not in Codespaces. The Whisper `base` model runs well on Intel CPU without a GPU.

---

## 12. Submission Checklist

### Code & Files
- [ ] `app.py` runs end-to-end without errors
- [ ] All modules in `core/`, `memory/`, `state/`, `ui/` present
- [ ] `pyproject.toml` lists all dependencies
- [ ] `.gitignore` excludes `.venv/`, `.env`, `chroma_db/`, `uploads/*.pdf`
- [ ] No hardcoded API keys anywhere
- [ ] All LLM output is in Spanish

### Features
- [ ] Text input → Spanish study sheet ✅
- [ ] PDF upload → Spanish study sheet ✅
- [ ] Practice questions generated in Spanish ✅
- [ ] ChromaDB stores and retrieves past topics ✅
- [ ] Milestone badges awarded on actions ✅
- [ ] Download button for study sheet ✅

### Documentation
- [ ] `README.md` with full setup instructions
- [ ] Workflow diagram included
- [ ] All functions have docstrings
- [ ] Non-obvious logic has inline comments

### Presentation Prep (5–10 min)
- [ ] Demo: paste notes → generate → take quiz → earn badge
- [ ] Demo: upload a PDF → show extraction → generate
- [ ] Demo: select saved topic → RAG memory retrieval
- [ ] Walk through the architecture diagram
- [ ] Explain one challenge (e.g. Spanish prompt engineering)
- [ ] Mention voice I/O as the next feature branch

### Submission
- [ ] GitHub link submitted on Canvas
- [ ] Named `FirstName_LastName_CapstoneAI`
- [ ] App runs entirely without paid APIs

---

*Compañero AI · CAP 942 — AI Application Development · `gitMiguel27/Compa-ero_AI`*
