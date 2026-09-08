import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

BASE_CHROMA_DIR = "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )


def build_vector_store(transcript: str, meeting_id: str) -> Chroma:
    persist_dir = os.path.join(BASE_CHROMA_DIR, meeting_id)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata={"meeting_id": meeting_id, "chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()

    return Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=f"meeting_{meeting_id}",
        persist_directory=persist_dir
    )


def load_vector_store(meeting_id: str) -> Chroma:
    persist_dir = os.path.join(BASE_CHROMA_DIR, meeting_id)

    embeddings = get_embeddings()

    return Chroma(
        collection_name=f"meeting_{meeting_id}",
        embedding_function=embeddings,
        persist_directory=persist_dir
    )


def get_retriever(vector_store: Chroma, k: int = 4):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
