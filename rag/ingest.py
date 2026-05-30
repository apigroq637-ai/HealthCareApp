import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from rag.chroma_db import get_vectorstore

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


def ingest_report(pdf_path: str, patient_email: str):
    """
    Ingest a PDF report into ChromaDB.
    """
    if not os.path.exists(pdf_path):
        return {"success": False, "message": "PDF file not found."}

    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            return {"success": False, "message": "No readable text found inside PDF."}

        chunks = splitter.split_documents(documents)

        for chunk in chunks:
            chunk.metadata["email"] = patient_email
            chunk.metadata["source"] = os.path.basename(pdf_path)

        db = get_vectorstore()
        db.add_documents(chunks)
        db.persist()

        return {
            "success": True,
            "message": "RAG ingestion successful.",
            "chunks": len(chunks),
            "filename": os.path.basename(pdf_path)
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
