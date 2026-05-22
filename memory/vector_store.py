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

    The collection_name acts like a table name - it groups related documents.
    Using one collection per app keeps things simple for the MVP.
    You could extend this to one collection per student in the future.

    Args:
        collection_name: Name of the Chromadb collection to use/create.

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

    Metadata is key - it lets us filter by topic later so the student's notes on "Fotosíntesis" don't bleed into their "Guerra Civil" notes.

    Args:
        chunks: List of text chunks from the ingestor.
        topic: The study topic (used as a metadata filter later).
        source: Where the content came from ('upload' or 'typed').

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

    This is the "retrieval" in RAG. We search ChromaDB for the k chunks most semantically similar to the query and returns them as a single context string to feed into our LLM prompt.

    Args:
        query: The search query (usually the topic or a question).
        topic: Optional filter - only search within a specific topic.
        k: Number of chunks to retrieve (4 is a good default).

    Returns:
        str: Retrieved chunks joined into a single context block. Returns empty string if nothing is found.
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
        
        #Join chunks with a separator for readability in the prompt
        return "\n\n---\n\n".join([doc.page_content for doc in results])

    except Exception as e:
        print(f"ChromaDB retrieval error: {e}")
        return ""

def get_stored_topics() -> list[str]:
    """
    Returns a list of unique topics stored in ChromaDB.

    Used in the UI sidebar to let students pick a past topic instead of re-uploading material.

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