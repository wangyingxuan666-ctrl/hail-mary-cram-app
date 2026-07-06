"""Explanation generator service using LLM with SSE streaming."""
import asyncio
from typing import AsyncGenerator

from openai import OpenAI

from config import settings
from prompts.explanation import EXPLANATION_SYSTEM_PROMPT, EXPLANATION_USER_TEMPLATE
from services.rag_service import retrieve_context
from services.frequency_analyzer import get_cached_frequency_table


_client: OpenAI = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


async def stream_explanation(
    question: str,
    session_history: list[dict] = None,
) -> AsyncGenerator[str, None]:
    """Stream a 6-step explanation for a question via SSE."""

    # Retrieve relevant context
    context = retrieve_context(question, k=settings.top_k_retrieval)

    # Get frequency info
    freq_table = get_cached_frequency_table()
    freq_info = "暂无频率数据"
    if freq_table.topics:
        freq_lines = []
        for t in freq_table.topics[:10]:
            freq_lines.append(f"- {t.topic_name}: {t.priority} ({t.frequency_count}/{t.total_years}年, {t.frequency_pct}%)")
        freq_info = "\n".join(freq_lines)

    user_prompt = EXPLANATION_USER_TEMPLATE.format(
        question=question,
        context=context,
        frequency_info=freq_info,
    )

    messages = [{"role": "system", "content": EXPLANATION_SYSTEM_PROMPT}]

    # Add recent chat history
    if session_history:
        for msg in session_history[-6:]:  # last 6 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_prompt})

    client = _get_client()
    stream = client.chat.completions.create(
        model=settings.model_name,
        messages=messages,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield f"data: {content}\n\n"
            await asyncio.sleep(0)  # yield to event loop

    yield "data: [DONE]\n\n"


async def generate_explanation(
    question: str,
    session_history: list[dict] = None,
) -> str:
    """Generate a non-streaming 6-step explanation."""
    text = ""
    async for chunk in stream_explanation(question, session_history):
        if chunk.startswith("data: ") and chunk != "data: [DONE]\n\n":
            text += chunk[6:].rstrip("\n")
    return text


async def generate_strategy(course_name: str = "") -> str:
    """Generate exam selection strategy based on frequency table."""
    freq_table = get_cached_frequency_table()

    if not freq_table.topics:
        return "请先上传真题并生成频率表。"

    topics_str = "\n".join([
        f"- {t.topic_name}: {t.priority} ({t.frequency_count}/{t.total_years}年, {t.frequency_pct}%)"
        for t in freq_table.topics
    ])

    client = _get_client()
    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": "你是一个考试策略专家。根据考点频率表，帮考生制定选题策略：哪些题必做、哪些题可选、哪些题可跳过。给出最佳组合和预期总分。"},
            {"role": "user", "content": f"课程: {course_name or freq_table.course_name}\n\n考点频率表:\n{topics_str}\n\n请给出选题策略（包括最佳组合、预期总分、可跳过的内容）。"},
        ],
        temperature=0.5,
        max_tokens=2048,
    )

    return response.choices[0].message.content or ""
