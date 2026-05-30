from rag.chroma_db import get_vectorstore


def retrieve_patient_context(email: str, query: str, k: int = 4):
    """
    Retrieve only patient-specific documents from ChromaDB.
    """

    db = get_vectorstore()

    docs = db.similarity_search(
        query=query,
        k=k,
        filter={"email": email}
    )

    if not docs:
        return "No uploaded reports found."

    return "\n\n".join(doc.page_content for doc in docs)