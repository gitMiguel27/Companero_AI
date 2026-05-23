# core/llm.py
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

load_dotenv()

def get_llm(temperature: float = 0.5) -> OllamaLLM:
    """
    Returns a configured Ollama LLM instance pointed at Llama 3.2.

    Temperature guide for this project:
        0.2-0.4 -> factual study sheets (we want accuracy, not creativity)
        0.5-0.6 -> practice questions (some variety is good)
        0.7+ -> conversational tone (future stretch goal)

    Args:
        temperature: Creativity dial (0.0 = deterministic, 1.0 = very creative)

    Returns:
        OllamaLLM: A LangChain-compatible LLM ready to call.
    """
    return OllamaLLM(
        model=os.getenv("MODEL_NAME", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "hhtp://localhost:11434"),
        temperature=temperature,
    )