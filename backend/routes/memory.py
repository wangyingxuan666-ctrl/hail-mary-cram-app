"""Memory routes for tracking user mastery progress."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.memory import MemoryStatus, UpdateMemoryRequest
from services.memory_service import (
    get_memory_status,
    update_memory,
    delete_memory_entry,
)

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("/status", response_model=MemoryStatus)
async def get_status():
    """Get current mastery tracking status."""
    return get_memory_status()


@router.post("/update")
async def update_entry(req: UpdateMemoryRequest):
    """Mark topic as mastered/confused/learning."""
    entry = update_memory(req.topic, req.status, req.notes)
    return JSONResponse(content=entry.model_dump(mode="json"))


@router.get("/summary")
async def get_summary():
    """Get progress summary."""
    status = get_memory_status()
    if status.total_topics == 0:
        pct = 0
    else:
        pct = round(status.mastered_count / status.total_topics * 100, 1)

    return JSONResponse(content={
        "mastered": status.mastered_count,
        "confused": status.confused_count,
        "total": status.total_topics,
        "mastered_pct": pct,
    })


@router.delete("/entry/{topic:path}")
async def delete_entry(topic: str):
    """Remove a memory entry."""
    ok = delete_memory_entry(topic)
    if not ok:
        raise HTTPException(status_code=404, detail="Entry not found")
    return JSONResponse(content={"status": "deleted"})
