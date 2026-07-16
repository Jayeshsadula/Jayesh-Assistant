"""
Chat endpoints.

POST /chat        -> non-streaming, returns the full assistant message (used by
                      simple integrations/tests, or clients that don't want SSE).
POST /chat/stream  -> SSE streaming, token-by-token, used by the React frontend.

Both endpoints share the same orchestration path: persist the user's message,
run the LangGraph orchestrator to assemble context (memory + RAG + tools),
then generate a response with Ollama, persist it, and return/stream it.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents.orchestrator import build_generation_messages
from app.authentication.dependencies import CurrentUser
from app.llm.ollama_client import get_ollama_client
from app.schemas.common import MessageRole
from app.schemas.conversation import ChatRequest, ChatResponse, MessagePublic
from app.schemas.user import UserInDB
from app.services.conversation_service import ConversationService
from app.streaming.sse import sse_token_stream
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


async def _prepare_conversation(
    payload: ChatRequest, current_user: UserInDB, service: ConversationService
) -> str:
    """Ensure a conversation exists, persist the user's message, return the conversation_id."""
    if payload.conversation_id:
        conversation = await service.get_conversation(
            conversation_id=payload.conversation_id, user_id=current_user.uid
        )
        conversation_id = conversation.conversation_id
    else:
        conversation = await service.create_conversation(
            user_id=current_user.uid, title="New Chat", model=payload.model
        )
        conversation_id = conversation.conversation_id

    await service.add_message(conversation_id, MessageRole.USER, payload.message)
    await service.maybe_set_title_from_first_message(conversation_id, payload.message)
    return conversation_id


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(payload: ChatRequest, current_user: UserInDB = CurrentUser) -> ChatResponse:
    service = ConversationService()
    conversation_id = await _prepare_conversation(payload, current_user, service)

    history_records = await service.get_recent_messages(conversation_id)
    # The message we just persisted is always the last record; slice it off rather than
    # matching on content, since two turns could legitimately share identical text.
    history = [
        {"role": m.role.value if hasattr(m.role, "value") else m.role, "content": m.content}
        for m in (history_records[:-1] if history_records else [])
    ]

    messages = await build_generation_messages(
        user_id=current_user.uid,
        model=payload.model,
        user_message=payload.message,
        history=history,
        use_memory=payload.use_memory,
        use_rag=payload.use_rag,
        document_ids=payload.document_ids,
    )

    ollama = get_ollama_client()
    full_text_parts = []
    async for token in ollama.stream_chat(model=payload.model, messages=messages):
        full_text_parts.append(token)
    full_text = "".join(full_text_parts)

    assistant_message = await service.add_message(
        conversation_id, MessageRole.ASSISTANT, full_text, model_used=payload.model
    )
    await service.touch_conversation(conversation_id)

    return ChatResponse(
        conversation_id=conversation_id,
        message=MessagePublic(**assistant_message.model_dump()),
    )


@router.post("/chat/stream", tags=["chat"])
async def chat_stream(payload: ChatRequest, current_user: UserInDB = CurrentUser) -> StreamingResponse:
    service = ConversationService()
    conversation_id = await _prepare_conversation(payload, current_user, service)

    history_records = await service.get_recent_messages(conversation_id)
    history = [
        {"role": m.role.value if hasattr(m.role, "value") else m.role, "content": m.content}
        for m in (history_records[:-1] if history_records else [])
    ]

    messages = await build_generation_messages(
        user_id=current_user.uid,
        model=payload.model,
        user_message=payload.message,
        history=history,
        use_memory=payload.use_memory,
        use_rag=payload.use_rag,
        document_ids=payload.document_ids,
    )

    ollama = get_ollama_client()
    token_generator = ollama.stream_chat(model=payload.model, messages=messages)

    async def event_stream():
        collected: list[str] = []

        async def _tap():
            async for token in token_generator:
                collected.append(token)
                yield token

        async for frame in sse_token_stream(_tap(), conversation_id):
            yield frame

        full_text = "".join(collected)
        if full_text:
            await service.add_message(
                conversation_id, MessageRole.ASSISTANT, full_text, model_used=payload.model
            )
            await service.touch_conversation(conversation_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": conversation_id,
        },
    )
