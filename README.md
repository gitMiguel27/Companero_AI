# 🧑‍🏫 Compañero_AI
### AI-Driven Personal Tutor for Spanish-Speaking Students
> CAP 942 - AI Application Development Capstone

Compañero AI is a locally-run AI tutor that helps Spanish-speaking students study more effectively. Upload a PDF or paste your notes and get an AI-generated study sheet and practice quiz - entirely in Spanish, with no paid APIs required.

## 🎯 Problem Statement

Spanish-speaking students often learn content in English but are tested in 
Spanish (e.g. NYS Regents exams). They face both a learning barrier and a 
language barrier simultaneously. Compañero AI bridges this gap by generating 
personalized study materials in Spanish from any uploaded content, making 
education more accessible and engaging.

## ✨ Features

- 📄 **Study Sheet Generator** — paste notes or upload a PDF and get a structured Spanish study sheet with key concepts, summary, and memory tips
- ❓ **Practice Quiz** — AI-generated questions with a reveal mechanic to test comprehension
- 🧠 **Session Memory** — ChromaDB stores past study sessions so students can revisit topics without re-uploading
- 🏆 **Milestone Badges** — reward system that tracks progress and awards badges for study activity
- 🌐 **Spanish-First Output** — all AI responses generated in Spanish by design
- 📚 **PDF Support** — upload real study materials like NYS Regents exam prep sheets

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core language |
| Ollama + Llama 3.2 | Local LLM with Spanish multilingual support |
| LangChain Core | LCEL prompt chaining and orchestration |
| pdfplumber | PDF text extraction with Spanish character support |
| ChromaDB | Local vector database for session memory |
| HuggingFace Embeddings | Local text embeddings (all-MiniLM-L6-v2) |
| Streamlit | Interactive UI |
| uv | Fast Python package management |

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installed
- [Ollama](https://ollama.com) installed

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/gitMiguel27/Companero_AI.git
cd Companero_AI
```

**2. Create and activate virtual environment**
```bash
uv venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
uv sync
```

**4. Create your .env file**
```bash
cat > .env << 'EOF'
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
EOF
```

**5. Pull the LLM model**
```bash
ollama pull llama3.2
```

**6. Start Ollama and run the app**
```bash
ollama serve &
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 🗺️ Application Workflow

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
│   ChromaDB       │   │      LangChain LCEL Chains    │
│  stores chunks   │   │  StudySheetChain              │
│  & embeddings    │   │  QuestionChain                │
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

## 🧠 Challenges & Lessons Learned

**LangChain version compatibility** — LangChain v1.3+ restructured its 
modules significantly. `LLMChain`, `langchain.prompts`, and `langchain.schema` 
were all deprecated. Migrated to LCEL pipe operator (`|`), `langchain_core`, 
and `langchain_ollama` throughout the project.

**protobuf conflict with ChromaDB** — ChromaDB's telemetry module caused a 
`TypeError` with newer protobuf versions. Resolved by setting 
`PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` in the environment.

**Git hygiene** — `.venv` was accidentally committed in the first push, 
bloating the repo to 2.63GB. Learned to always create `.gitignore` before 
the first `git add .`, and used `git rm --cached` and `git reset --soft` 
to rewrite clean history.

**Prompt engineering in Spanish** — Writing prompts entirely in Spanish 
improved output consistency. Adding `"Responde ÚNICAMENTE en español"` at 
the end of each prompt reduced language drift significantly.

**Separation of concerns** — Refactored `generate_study_sheet_from_pdf` to 
return a tuple `(study_sheet, pdf_content)` instead of adding PDF logic to 
the sidebar, keeping each module responsible for its own domain.

## 📁 Project Structure

```
companero-ai/
├── app.py                  # Streamlit entry point
├── core/
│   ├── ingestor.py         # PDF extraction and text chunking
│   ├── llm.py              # Ollama LLM configuration
│   ├── prompts.py          # Spanish prompt templates
│   ├── questions.py        # Practice question generation
│   └── study_sheet.py      # Study sheet generation chains
├── memory/
│   ├── embeddings.py       # HuggingFace embedding config
│   └── vector_store.py     # ChromaDB operations
├── state/
│   └── session.py          # Session state and badge system
└── ui/
    ├── sidebar.py          # Input controls
    ├── study_view.py       # Study sheet display
    ├── quiz_view.py        # Practice quiz tab
    └── rewards_view.py     # Badges and progress tab
```