"""Document loading service: PDF/DOCX/TXT extraction and chunking."""
import os
import uuid
import json
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument

from config import settings


# Try imports for optional formats
try:
    from langchain_community.document_loaders import Docx2txtLoader
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def _generate_id() -> str:
    return str(uuid.uuid4())[:8]


def _get_docs_index_path() -> Path:
    return settings.get_data_path("documents_index.json")


def _load_docs_index() -> dict:
    p = _get_docs_index_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _save_docs_index(index: dict) -> None:
    _get_docs_index_path().write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_text_pdf(file_path: str) -> tuple[str, int]:
    """Extract text from PDF. Tries PyPDFLoader first, then pdfplumber."""
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text = "\n\n".join(d.page_content for d in docs)
        page_count = len(docs)
        if text.strip():
            return text, page_count
    except Exception:
        pass

    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages_text.append(t)
                text = "\n\n".join(pages_text)
                return text, len(pdf.pages)
        except Exception:
            pass

    # Fallback: try reading as raw text
    try:
        loader = PyPDFLoader(file_path, extract_images=False)
        docs = loader.load()
        text = "\n\n".join(d.page_content for d in docs)
        return text, len(docs)
    except Exception:
        return "", 0


def _extract_text_docx(file_path: str) -> tuple[str, int]:
    """Extract text from DOCX."""
    if not HAS_DOCX:
        raise ImportError("docx2txt not installed. Run: pip install docx2txt")
    loader = Docx2txtLoader(file_path)
    docs = loader.load()
    text = "\n\n".join(d.page_content for d in docs)
    return text, 1


def _extract_text_txt(file_path: str) -> tuple[str, int]:
    """Extract text from TXT."""
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    text = "\n\n".join(d.page_content for d in docs)
    lines = text.split("\n")
    page_count = max(1, len(lines) // 50)
    return text, page_count


def extract_text(file_path: str) -> tuple[str, int]:
    """Extract text from a file. Returns (text, page_count)."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_text_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_text_docx(file_path)
    elif ext == ".txt":
        return _extract_text_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.max_chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )


def process_document(file_path: str, filename: str, doc_type: str) -> dict:
    """
    Process an uploaded document:
    1. Extract text
    2. Split into chunks
    3. Store in documents index
    Returns document metadata dict.
    """
    text, page_count = extract_text(file_path)
    doc_id = _generate_id()

    splitter = get_text_splitter()
    lc_docs = [LCDocument(page_content=text, metadata={"source": filename, "doc_id": doc_id, "doc_type": doc_type})]
    chunks = splitter.split_documents(lc_docs)

    # Add page/position metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    doc_entry = {
        "id": doc_id,
        "filename": filename,
        "doc_type": doc_type,
        "page_count": page_count,
        "chunk_count": len(chunks),
        "content_preview": text[:300] + ("..." if len(text) > 300 else ""),
        "text": text,
        "chunks": [
            {"index": i, "content": c.page_content, "metadata": c.metadata}
            for i, c in enumerate(chunks)
        ],
        "processed": True,
    }

    index = _load_docs_index()
    index[doc_id] = doc_entry
    _save_docs_index(index)

    return doc_entry


def get_all_documents() -> list[dict]:
    return list(_load_docs_index().values())


def get_document(doc_id: str) -> Optional[dict]:
    return _load_docs_index().get(doc_id)


def delete_document(doc_id: str) -> bool:
    index = _load_docs_index()
    if doc_id in index:
        del index[doc_id]
        _save_docs_index(index)
        return True
    return False


def get_all_materials() -> list[dict]:
    return [d for d in get_all_documents() if d["doc_type"] == "material"]


def get_all_exams() -> list[dict]:
    return [d for d in get_all_documents() if d["doc_type"] == "exam"]
