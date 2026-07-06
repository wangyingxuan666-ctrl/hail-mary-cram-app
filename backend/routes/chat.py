"""Chat routes for interactive exam Q&A with SSE streaming."""
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse

from models.chat import (
    ChatMessage, ChatSession,
    SendMessageRequest, StartSessionRequest, ExplainTopicRequest,
)
from services.explanation_generator import stream_explanation, generate_explanation
from services.rag_service import retrieve_context
from config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory session store (backed by disk)
_sessions: dict[str, ChatSession] = {}


def _get_sessions_path():
    return settings.get_data_path("sessions", "_index.json")


def _load_sessions():
    global _sessions
    p = _get_sessions_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for sid, sdata in data.items():
                session = ChatSession(
                    id=sdata["id"],
                    exam_paper=sdata.get("exam_paper", ""),
                    messages=[ChatMessage(**m) for m in sdata.get("messages", [])],
                    created_at=datetime.fromisoformat(sdata["created_at"]) if sdata.get("created_at") else datetime.now(),
                )
                _sessions[sid] = session
        except Exception:
            pass


def _save_sessions():
    p = _get_sessions_path()
    data = {}
    for sid, session in _sessions.items():
        data[sid] = {
            "id": session.id,
            "exam_paper": session.exam_paper,
            "messages": [m.model_dump(mode="json") for m in session.messages],
            "created_at": session.created_at.isoformat(),
        }
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# Load sessions on module init
_load_sessions()


@router.post("/start", response_model=ChatSession)
async def start_session(req: StartSessionRequest = StartSessionRequest()):
    """Start a new chat session."""
    session = ChatSession(exam_paper=req.exam_paper)
    _sessions[session.id] = session
    _save_sessions()
    return session


@router.post("/send")
async def send_message(req: SendMessageRequest):
    """Send a message and stream back the 6-step explanation via SSE."""
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[req.session_id]

    # Add user message
    user_msg = ChatMessage(
        role="user",
        content=req.message,
        question_ref=req.question_ref,
    )
    session.messages.append(user_msg)

    # Get history for context
    history = [
        {"role": m.role, "content": m.content}
        for m in session.messages[-10:]
    ]

    async def event_stream():
        full_response = ""
        async for chunk in stream_explanation(req.message, history):
            if chunk.startswith("data: ") and chunk != "data: [DONE]\n\n":
                chunk_text = chunk[6:].rstrip("\n")
                full_response += chunk_text
            yield chunk

        # Save assistant message
        assistant_msg = ChatMessage(
            role="assistant",
            content=full_response,
            question_ref=req.question_ref,
        )
        session.messages.append(assistant_msg)
        _sessions[session.id] = session
        _save_sessions()

    return EventSourceResponse(event_stream())


@router.get("/{session_id}/history")
async def get_history(session_id: str):
    """Get chat history for a session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return _sessions[session_id]


@router.post("/explain-topic")
async def explain_topic(req: ExplainTopicRequest):
    """Explain a specific topic with the 6-step method."""
    try:
        if req.include_rag:
            context = retrieve_context(req.topic)
            question = f"请详细讲解以下考点：{req.topic}\n\n相关课件内容：\n{context}"
        else:
            question = f"请详细讲解以下考点：{req.topic}"

        explanation = await generate_explanation(question)
        return JSONResponse(content={"topic": req.topic, "explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讲解生成失败: {str(e)}")


@router.get("/sessions")
async def list_sessions():
    """List all chat sessions."""
    return [
        {
            "id": s.id,
            "exam_paper": s.exam_paper,
            "message_count": len(s.messages),
            "created_at": s.created_at.isoformat(),
        }
        for s in _sessions.values()
    ]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    if session_id in _sessions:
        del _sessions[session_id]
        _save_sessions()
        return JSONResponse(content={"status": "deleted"})
    raise HTTPException(status_code=404, detail="Session not found")
