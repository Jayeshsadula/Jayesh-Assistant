"""Long-term memory endpoints: create, list, delete user facts/preferences."""

from typing import List

from fastapi import APIRouter

from app.authentication.dependencies import CurrentUser
from app.memory.memory_service import MemoryService
from app.schemas.memory import MemoryCreateRequest, MemoryPublic
from app.schemas.user import UserInDB

router = APIRouter()


@router.post("/memory", response_model=MemoryPublic, tags=["memory"])
async def create_memory(payload: MemoryCreateRequest, current_user: UserInDB = CurrentUser) -> MemoryPublic:
    service = MemoryService()
    record = await service.add_memory(
        user_id=current_user.uid,
        memory_type=payload.memory_type,
        content=payload.content,
    )
    return MemoryPublic(**record.model_dump())


@router.get("/memory", response_model=List[MemoryPublic], tags=["memory"])
async def list_memory(current_user: UserInDB = CurrentUser) -> List[MemoryPublic]:
    service = MemoryService()
    return await service.list_memories(user_id=current_user.uid)


@router.delete("/memory/{memory_id}", status_code=204, tags=["memory"])
async def delete_memory(memory_id: str, current_user: UserInDB = CurrentUser) -> None:
    service = MemoryService()
    await service.delete_memory(user_id=current_user.uid, memory_id=memory_id)
