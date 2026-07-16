"""Conversation management endpoints: list, create, rename, delete, list messages."""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.authentication.dependencies import CurrentUser
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationPublic,
    ConversationRenameRequest,
    MessagePublic,
)
from app.schemas.user import UserInDB
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationPublic], tags=["conversations"])
async def list_conversations(
    search: Optional[str] = Query(default=None, description="Filter conversations by title"),
    current_user: UserInDB = CurrentUser,
) -> List[ConversationPublic]:
    service = ConversationService()
    return await service.list_conversations(user_id=current_user.uid, search=search)


@router.post("/conversations", response_model=ConversationPublic, tags=["conversations"])
async def create_conversation(
    payload: ConversationCreateRequest,
    current_user: UserInDB = CurrentUser,
) -> ConversationPublic:
    service = ConversationService()
    conversation = await service.create_conversation(
        user_id=current_user.uid, title=payload.title or "New Chat", model=payload.model
    )
    return ConversationPublic(**conversation.model_dump())


@router.patch("/conversations/{conversation_id}", response_model=ConversationPublic, tags=["conversations"])
async def rename_conversation(
    conversation_id: str,
    payload: ConversationRenameRequest,
    current_user: UserInDB = CurrentUser,
) -> ConversationPublic:
    service = ConversationService()
    return await service.rename_conversation(
        conversation_id=conversation_id, user_id=current_user.uid, title=payload.title
    )


@router.delete("/conversations/{conversation_id}", status_code=204, tags=["conversations"])
async def delete_conversation(conversation_id: str, current_user: UserInDB = CurrentUser) -> None:
    service = ConversationService()
    await service.delete_conversation(conversation_id=conversation_id, user_id=current_user.uid)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessagePublic],
    tags=["conversations"],
)
async def get_conversation_messages(
    conversation_id: str, current_user: UserInDB = CurrentUser
) -> List[MessagePublic]:
    service = ConversationService()
    # Ensures the conversation belongs to the requesting user before returning messages.
    await service.get_conversation(conversation_id=conversation_id, user_id=current_user.uid)
    return await service.list_messages(conversation_id)
