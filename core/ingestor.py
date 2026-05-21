import pdfplumber
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file using pdfplumber.
    
    pdfplumber handles Spanish characters (accents, ñ, etc.) correctly, which is why we chose it over PyPDF2 for this project.
    
    Args:
        file_path: Path to the PDF file on disk.
        
    Returns:
        str: All extracted text concatenated, page by page. Returns empty string if extraction fails.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: # Some pages are images - skif if None
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits a long text into overlapping chunks for ChromaDB strorage.
    
    Why overlap? If a key concept spans two chunks, overlap ensures it's captured in at least one chunk's context window. Without overlap, you'd lsoe information at chunk boundaries.
    
    Args:
        text: The full text to split.
        chunk_size: Target character count per chunk (500 ≈ ~100 words).
        overlap: How many characters to repeat between consecutive chunks.
        
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
        if chunk.strip(): # Skip chunks that are only whitespace
            chunks.append(chunk.strip())
        start += chunk_size - overlap # Step forward, minus the overlap
    
    return chunks

def ingest_uploaded_file(file_path: str) -> list[str]:
    """
    Full pipeline: PDF file -> extracted text -> chunks.
    
    This is the function the rest of the app calls.
    It abstracts away whether the source is a PDF or plain text.

    Args:
        file_path: Path to the uploaded file.

    Returns:
        list[str]: Text chunks ready for ChromaDB storage.
    """
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        text = extracted_text_from_pdf(file_path)
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
