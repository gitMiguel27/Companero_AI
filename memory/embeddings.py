# memory/embeddings.py
from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    """
    Returns a sentence-transformer embedding model.

    We use 'all-MiniLM-L6-v2' because:
    - It's small (~80mb), fast, and runs on CPU
    - It supports multilingual text including Spanish
    - It's the most common embedding model for local RAG apps

    This model downloads once on first use (~80mb).
    Subsequent uses load from local cache.

    Returns:
        SentenceTransformerEmbeddings: An embedding function compatible with LangChain and ChromaDB.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")