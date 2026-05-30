import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Railway has an ephemeral filesystem — /tmp persists within a session.
# For production persistence, mount a Railway Volume and set CHROMA_PATH env var.
CHROMA_PATH = os.getenv("CHROMA_PATH", "/tmp/chroma_db")

_embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def get_vectorstore():
    """
    Returns a persistent Chroma vector store instance.
    Reused by both ingestion and retrieval layers.
    """
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=_embedding_model
    )


def get_embedding_model():
    return _embedding_model
