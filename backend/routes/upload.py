"""Upload routes for document management."""
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from config import settings
from models.document import DocumentResponse, DocumentListResponse
from services import document_loader
from services.vector_store import add_documents, rebuild_index

router = APIRouter(prefix="/api", tags=["upload"])


UPLOAD_DIR = settings.get_data_path("uploads")


@router.post("/upload/materials", response_model=DocumentResponse)
async def upload_materials(file: UploadFile = File(...)):
    """Upload course materials (PDF/DOCX/TXT)."""
    return await _handle_upload(file, "material")


@router.post("/upload/exams", response_model=DocumentResponse)
async def upload_exams(file: UploadFile = File(...)):
    """Upload exam papers (PDF/DOCX/TXT)."""
    return await _handle_upload(file, "exam")


async def _handle_upload(file: UploadFile, doc_type: str) -> DocumentResponse:
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".doc", ".txt"):
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    # Save file
    file_bytes = await file.read()
    save_path = str(UPLOAD_DIR / file.filename)
    # Ensure unique filename
    counter = 1
    while os.path.exists(save_path):
        stem = Path(file.filename).stem
        save_path = str(UPLOAD_DIR / f"{stem}_{counter}{ext}")
        counter += 1

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Process document
    try:
        doc_entry = document_loader.process_document(
            save_path,
            Path(save_path).name,
            doc_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    # Add chunks to vector store (only for materials)
    if doc_type == "material" and doc_entry.get("chunks"):
        try:
            add_documents(doc_entry["chunks"], doc_entry["id"])
        except Exception as e:
            # Non-fatal: document is stored, just not indexed yet
            print(f"Warning: failed to add chunks to vector store: {e}")

    return DocumentResponse(
        id=doc_entry["id"],
        filename=doc_entry["filename"],
        doc_type=doc_entry["doc_type"],
        page_count=doc_entry["page_count"],
        chunk_count=doc_entry["chunk_count"],
        content_preview=doc_entry["content_preview"],
        processed=doc_entry["processed"],
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    docs = document_loader.get_all_documents()
    responses = [
        DocumentResponse(
            id=d["id"],
            filename=d["filename"],
            doc_type=d["doc_type"],
            page_count=d["page_count"],
            chunk_count=d["chunk_count"],
            content_preview=d["content_preview"],
            processed=d["processed"],
        )
        for d in docs
    ]
    return DocumentListResponse(documents=responses, total=len(responses))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its vectors."""
    doc = document_loader.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete uploaded file
    file_path = UPLOAD_DIR / doc["filename"]
    if file_path.exists():
        os.remove(file_path)

    # Remove from index
    document_loader.delete_document(doc_id)

    # Rebuild vector index
    remaining = document_loader.get_all_documents()
    rebuild_index(remaining)

    return JSONResponse(content={"status": "deleted", "id": doc_id})


@router.post("/documents/rebuild-index")
async def rebuild_vector_index():
    """Rebuild the FAISS index from all uploaded materials."""
    docs = document_loader.get_all_documents()
    count = rebuild_index(docs)
    return JSONResponse(content={"status": "ok", "chunk_count": count})
