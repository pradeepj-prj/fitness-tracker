from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from openai import OpenAI
from sqlalchemy.orm import Session

from app.agent.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS
from app.config import settings
from app.models import AgentConversation, AgentMessage
from app.schemas import AgentChatResponse, AgentMessageResponse


MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_TOOL_ROUNDS = 6


def _read_context_file(name: str) -> str:
    path = Path(__file__).resolve().parents[1] / "agent_context" / name
    return path.read_text(encoding="utf-8")


def _system_prompt(profile: str, summary: str | None) -> str:
    rules = _read_context_file("01-agent-operating-rules.md")
    references = _read_context_file("02-calorie-reference-library.md")
    brief = _read_context_file("AGENT_BRIEF.md")
    summary_block = summary or "No older conversation summary yet."
    return f"""You are Pebble, a warm and practical calorie tracking assistant.

Active profile: {profile}

Conversation summary outside the recent message window:
{summary_block}

Use the tracker tools for reads and writes. Do not claim an entry was logged unless a tool
call succeeded. Do not use external food search APIs. Use package labels, weighed quantities,
the reference library, and conservative manual estimates. If an estimate is too ambiguous,
ask one brief clarifying question. A directly reported weigh-in is data: write it.

If asked whether something was already logged or saved, rely on tracker state: use recent
tool results in the conversation context or call list_entries/get_deficit before correcting
yourself. Never say a saved entry was not saved unless a read tool confirms that.
Zero-calorie drinks such as Coke Zero can be logged as 0 calories from the item name alone;
do not ask for volume unless the user wants serving details unrelated to calories.
If the user asks about a cup/container measurement, answer only that measurement question
unless they explicitly ask you to log food.

When you log or correct food, reply with what changed, today's total, and calories remaining.
Keep replies brief, human, and useful.

--- Agent operating rules ---
{rules}

--- API brief ---
{brief}

--- Calorie reference library ---
{references}
"""


def _get_or_create_conversation(db: Session, conversation_id: str | None, profile: str) -> AgentConversation:
    if conversation_id:
        row = db.query(AgentConversation).filter(AgentConversation.id == conversation_id).first()
        if row:
            return row

    row = AgentConversation(id=conversation_id or uuid4().hex, profile=profile)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _recent_messages(db: Session, conversation_id: str) -> list[AgentMessage]:
    return (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation_id)
        .order_by(AgentMessage.created_at.desc())
        .limit(settings.AGENT_CONTEXT_MESSAGE_LIMIT)
        .all()
    )[::-1]


def _message_content_for_model(row: AgentMessage) -> str:
    if row.role != "assistant" or not row.tool_summary:
        return row.content
    return (
        f"{row.content}\n\n"
        "[Internal tracker tool results from this assistant turn; use these as factual DB state, "
        "but do not quote them verbatim to the user.]\n"
        f"{row.tool_summary}"
    )


def _response_messages(db: Session, conversation_id: str) -> list[AgentMessageResponse]:
    rows = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation_id)
        .order_by(AgentMessage.created_at.desc())
        .limit(20)
        .all()
    )[::-1]
    return [
        AgentMessageResponse(role=row.role, content=row.content, created_at=row.created_at)
        for row in rows
    ]


def _trim_transcript(db: Session, conversation: AgentConversation) -> None:
    retention = max(settings.AGENT_TRANSCRIPT_RETENTION_LIMIT, settings.AGENT_CONTEXT_MESSAGE_LIMIT)
    count = db.query(AgentMessage).filter(AgentMessage.conversation_id == conversation.id).count()
    overflow = count - retention
    if overflow <= 0:
        return

    old_rows = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation.id)
        .order_by(AgentMessage.created_at.asc())
        .limit(overflow)
        .all()
    )
    compact_lines = [
        f"{row.created_at.isoformat()} {row.role}: {row.content[:500]}"
        for row in old_rows
        if row.content
    ]
    joined = "\n".join(compact_lines)
    existing = conversation.summary or ""
    conversation.summary = (existing + "\n" + joined).strip()[-5000:]
    for row in old_rows:
        db.delete(row)
    db.commit()


async def _image_to_content_part(upload: UploadFile) -> dict[str, Any]:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail=f"{upload.filename or 'image'} is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail=f"{upload.filename or 'image'} is larger than 8 MB")

    content_type = upload.content_type or "image/jpeg"
    encoded = base64.b64encode(data).decode("ascii")
    return {
        "type": "input_image",
        "image_url": f"data:{content_type};base64,{encoded}",
        "detail": "auto",
    }


def _item_to_dict(item: Any) -> dict[str, Any]:
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_none=True)
    if isinstance(item, dict):
        return item
    return dict(item)


def _tool_calls(response: Any) -> list[Any]:
    return [
        item for item in getattr(response, "output", [])
        if getattr(item, "type", None) == "function_call" or (isinstance(item, dict) and item.get("type") == "function_call")
    ]


def _output_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text

    chunks: list[str] = []
    for item in getattr(response, "output", []):
        item_dict = _item_to_dict(item)
        if item_dict.get("type") != "message":
            continue
        for part in item_dict.get("content", []):
            if part.get("type") in {"output_text", "text"} and part.get("text"):
                chunks.append(part["text"])
    return "\n".join(chunks).strip()


def _call_tool(db: Session, call: Any) -> dict[str, Any]:
    name = getattr(call, "name", None) or call.get("name")
    raw_args = getattr(call, "arguments", None) or call.get("arguments") or "{}"
    arguments = json.loads(raw_args)
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    result = TOOL_FUNCTIONS[name](db, **arguments)
    return {"tool": name, "arguments": arguments, "result": result}


async def chat(
    db: Session,
    *,
    profile: str,
    message: str,
    conversation_id: str | None,
    images: list[UploadFile],
) -> AgentChatResponse:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    conversation = _get_or_create_conversation(db, conversation_id, profile)

    db.add(AgentMessage(conversation_id=conversation.id, profile=profile, role="user", content=message))
    db.commit()

    content_parts: list[dict[str, Any]] = [{"type": "input_text", "text": message}]
    for upload in images:
        content_parts.append(await _image_to_content_part(upload))

    input_items: list[dict[str, Any]] = [
        {"role": "system", "content": _system_prompt(profile, conversation.summary)},
    ]
    for row in _recent_messages(db, conversation.id):
        input_items.append({"role": row.role, "content": _message_content_for_model(row)})
    input_items[-1] = {"role": "user", "content": content_parts}

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    tool_summaries: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            input=input_items,
            tools=TOOL_SCHEMAS,
            store=False,
        )

        calls = _tool_calls(response)
        if not calls:
            reply = _output_text(response)
            db.add(
                AgentMessage(
                    conversation_id=conversation.id,
                    profile=profile,
                    role="assistant",
                    content=reply,
                    tool_summary="\n".join(tool_summaries) or None,
                )
            )
            db.commit()
            _trim_transcript(db, conversation)
            return AgentChatResponse(
                conversation_id=conversation.id,
                profile=profile,
                reply=reply,
                messages=_response_messages(db, conversation.id),
            )

        input_items.extend(_item_to_dict(item) for item in getattr(response, "output", []))
        for call in calls:
            try:
                tool_result = _call_tool(db, call)
            except Exception as exc:
                tool_result = {"error": str(exc)}
            tool_summaries.append(json.dumps(tool_result, default=str)[:1000])
            call_id = getattr(call, "call_id", None) or call.get("call_id")
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(tool_result, default=str),
                }
            )

    raise HTTPException(status_code=500, detail="Agent reached the tool-call limit")
