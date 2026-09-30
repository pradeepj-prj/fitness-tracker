from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.agent.service import chat
from app.database import get_db
from app.models import AgentConversation
from app.schemas import AgentChatResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    message: Annotated[str, Form(min_length=1)],
    profile: Annotated[str, Form(min_length=1, max_length=50)] = "vidhi",
    conversation_id: Annotated[Optional[str], Form()] = None,
    images: Annotated[Optional[List[UploadFile]], File()] = None,
    db: Session = Depends(get_db),
):
    return await chat(
        db,
        profile=profile,
        message=message,
        conversation_id=conversation_id,
        images=images or [],
    )


@router.get("/conversations/{conversation_id}", response_model=AgentChatResponse)
def get_conversation(
    conversation_id: str,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    from app.agent.service import _response_messages

    conversation = (
        db.query(AgentConversation)
        .filter(AgentConversation.id == conversation_id, AgentConversation.profile == profile)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return AgentChatResponse(
        conversation_id=conversation_id,
        profile=profile,
        reply="",
        messages=_response_messages(db, conversation_id),
    )
