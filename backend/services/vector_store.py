"""Vector store service using FAISS for document retrieval."""
import json
import pickle
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument
from langchain_core.embeddings import Embeddings
from openai import OpenAI

from config import settings


class DeepSeekEmbeddings(Embeddings):
    """Custom embeddings using DeepSeek API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        # Process in batches of 20
        for i in range(0, len(texts), 20):
            batch = texts[i:i + 20]
            response = self.client.embeddings.create(
                model="deepseek-chat",
                input=batch,
            )
            embeddings.extend([d.embedding for d in response.data])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="deepseek-chat",
            input=[text],
        )
        return response.data[0].embedding


_embeddings: Optional[DeepSeekEmbeddings] = None
_vector_store: Optional[FAISS] = None


def _get_embeddings() -> DeepSeekEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = DeepSeekEmbeddings()
    return _embeddings


def _get_index_dir() -> Path:
    return settings.get_data_path("vectors")


def _get_index_path() -> Path:
    return _get_index_dir() / "faiss_index"


def _get_metadata_path() -> Path:
    return _get_index_dir() / "metadata.json"


def get_vector_store() -> FAISS:
    global _vector_store
    if _vector_store is None:
        idx_path = _get_index_path()
        if idx_path.exists():
            _vector_store = FAISS.load_local(
                str(_get_index_dir()),
                _get_embeddings(),
                index_name="faiss_index",
                allow_dangerous_deserialization=True,
            )
        else:
            # Create empty store with a placeholder
            placeholder = LCDocument(page_content="placeholder", metadata={})
            _vector_store = FAISS.from_documents(
                [placeholder], _get_embeddings()
            )
    return _vector_store


def add_documents(chunks: list[dict], doc_id: str) -> int:
    """Add document chunks to vector store. Returns number of chunks added."""
    lc_docs = []
    for chunk in chunks:
        lc_docs.append(LCDocument(
            page_content=chunk["content"],
            metadata={**chunk.get("metadata", {}), "doc_id": doc_id},
        ))

    store = get_vector_store()
    store.add_documents(lc_docs)
    _save()
    return len(lc_docs)


def similarity_search(query: str, k: int = None, filter_doc_type: Optional[str] = None) -> list[dict]:
    """Search for relevant document chunks."""
    if k is None:
        k = settings.top_k_retrieval

    store = get_vector_store()
    results = store.similarity_search(query, k=k)

    output = []
    for doc in results:
        if doc.page_content == "placeholder":
            continue
        output.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
        })
    return output


def delete_by_doc_id(doc_id: str) -> None:
    """Delete all chunks for a document from the vector store."""
    global _vector_store
    store = get_vector_store()
    doc_ids_to_keep = []

    # FAISS doesn't support direct deletion, so we rebuild
    # Get all docs from the metadata
    meta_path = _get_metadata_path()
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    else:
        meta = {"docs": []}


def rebuild_index(documents: list[dict]) -> int:
    """Rebuild the FAISS index from all documents."""
    global _vector_store

    all_chunks = []
    for doc in documents:
        for chunk in doc.get("chunks", []):
            all_chunks.append(LCDocument(
                page_content=chunk["content"],
                metadata={**chunk.get("metadata", {}), "doc_id": doc["id"]},
            ))

    if not all_chunks:
        all_chunks = [LCDocument(page_content="placeholder", metadata={})]

    _vector_store = FAISS.from_documents(all_chunks, _get_embeddings())
    _save()
    return len(all_chunks)


def _save() -> None:
    store = get_vector_store()
    store.save_local(str(_get_index_dir()), index_name="faiss_index")


def get_vector_count() -> int:
    store = get_vector_store()
    return store.index.ntotal
