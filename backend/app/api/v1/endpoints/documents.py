"""Document upload endpoints. Ingestion (chunk + embed + index) runs as a background task
so the upload response returns immediately with status="processing"."""

from typing import List

from fastapi import APIRouter, BackgroundTasks, UploadFile

from app.authentication.dependencies import CurrentUser
from app.rag.ingestion_service import IngestionService
from app.schemas.document import DocumentPublic
from app.schemas.user import UserInDB
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentPublic, tags=["documents"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    current_user: UserInDB = CurrentUser,
) -> DocumentPublic:
    service = DocumentService()
    document = await service.save_upload(user_id=current_user.uid, upload=file)

    ingestion_service = IngestionService()
    background_tasks.add_task(
        ingestion_service.ingest,
        document_id=document.document_id,
        user_id=current_user.uid,
        file_path=document.file_path,
        content_type=document.content_type,
    )

    return DocumentPublic(**document.model_dump())


@router.get("/documents", response_model=List[DocumentPublic], tags=["documents"])
async def list_documents(current_user: UserInDB = CurrentUser) -> List[DocumentPublic]:
    service = DocumentService()
    return await service.list_documents(user_id=current_user.uid)


@router.delete("/documents/{document_id}", status_code=204, tags=["documents"])
async def delete_document(document_id: str, current_user: UserInDB = CurrentUser) -> None:
    service = DocumentService()
    await service.delete_document(user_id=current_user.uid, document_id=document_id)
