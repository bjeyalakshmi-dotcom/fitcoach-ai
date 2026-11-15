"""
RAG Engine — embeds queries and retrieves relevant fitness knowledge from Pinecone.
"""
import os
from openai import OpenAI

_client = None
_index  = None

PINECONE_INDEX = "fitcoach-knowledge"
EMBED_MODEL    = "text-embedding-3-small"
TOP_K          = 3


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def _get_index():
    global _index
    if _index is None:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        _index = pc.Index(PINECONE_INDEX)
    return _index


def embed(text: str) -> list[float]:
    """Return embedding vector for a text string."""
    response = _get_client().embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Embed the query and retrieve top-K matching chunks from Pinecone.
    Returns list of { "text": str, "score": float, "metadata": dict }
    """
    try:
        vector = embed(query)
        index  = _get_index()
        result = index.query(vector=vector, top_k=top_k, include_metadata=True)
        chunks = []
        for match in result.matches:
            chunks.append({
                "text":     match.metadata.get("text", ""),
                "score":    round(match.score, 3),
                "metadata": match.metadata,
            })
        return chunks
    except Exception as e:
        # Graceful fallback — return empty if Pinecone is unavailable
        print(f"[RAG] Retrieval failed: {e}")
        return []


def build_context(query: str) -> str:
    """
    Retrieve relevant chunks and format them as a context block
    to inject into an LLM prompt.
    """
    chunks = retrieve(query)
    if not chunks:
        return ""
    lines = ["[Relevant fitness knowledge retrieved from knowledge base:]"]
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"{i}. {chunk['text']}")
    return "\n".join(lines)
