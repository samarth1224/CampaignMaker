"""Authenticated endpoints for the user's brand and campaign knowledge base."""

from __future__ import annotations

import uuid
from pathlib import Path

import anyio
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app import config
from app.models.campaign import Campaign
from app.models.usermodel import User
from app.services.knowledge_base import (
    DocumentNotFoundError,
    DocumentSummary,
    EmbeddingError,
    KnowledgeBaseError,
    UnsupportedDocumentError,
    knowledge_base,
)
from app.utility.dependencies import verify_user_access_token

router = APIRouter(prefix="/documents", tags=["Documents"])


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    uploaded_at: str
    campaign_id: str | None = None


@router.post("/", response_model=list[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: list[UploadFile] = File(...),
    campaign_id: str | None = Form(default=None),
    user: User = Depends(verify_user_access_token),
):
    """Parse and index one or more documents for the authenticated user."""
    if not files:
        raise HTTPException(status_code=422, detail="Upload at least one document.")
    if len(files) > config.RAG_MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=422,
            detail=f"Upload no more than {config.RAG_MAX_FILES_PER_UPLOAD} documents at once.",
        )

    validated_campaign_id = await _validate_campaign_id(campaign_id, user)
    uploaded: list[DocumentSummary] = []
    for upload in files:
        filename = _safe_filename(upload.filename)
        if Path(filename).suffix.lower() not in config.RAG_SUPPORTED_EXTENSIONS:
            allowed = ", ".join(sorted(config.RAG_SUPPORTED_EXTENSIONS))
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported document type. Use: {allowed}.",
            )
        contents = await upload.read(config.RAG_MAX_DOCUMENT_BYTES + 1)
        await upload.close()
        if len(contents) > config.RAG_MAX_DOCUMENT_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"'{filename}' exceeds the {config.RAG_MAX_DOCUMENT_SIZE_MB} MB file limit.",
            )
        try:
            summary = await anyio.to_thread.run_sync(
                lambda: knowledge_base.ingest(
                    user_id=str(user.public_id),
                    filename=filename,
                    contents=contents,
                    campaign_id=validated_campaign_id,
                )
            )
            uploaded.append(summary)
        except EmbeddingError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (KnowledgeBaseError, UnsupportedDocumentError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return [DocumentResponse(**summary.__dict__) for summary in uploaded]


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(user: User = Depends(verify_user_access_token)):
    """List documents available as context for this user's campaigns."""
    try:
        documents = await anyio.to_thread.run_sync(
            lambda: knowledge_base.list_documents(user_id=str(user.public_id))
        )
    except KnowledgeBaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return [DocumentResponse(**summary.__dict__) for summary in documents]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user: User = Depends(verify_user_access_token),
):
    """Remove a document and all of its vector chunks."""
    try:
        uuid.UUID(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid document ID format.") from exc

    try:
        await anyio.to_thread.run_sync(
            lambda: knowledge_base.delete_document(
                user_id=str(user.public_id), document_id=document_id
            )
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except KnowledgeBaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def _validate_campaign_id(campaign_id: str | None, user: User) -> str | None:
    if campaign_id is None:
        return None
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="campaign_id must be a valid UUID.") from exc
    campaign = await Campaign.find_one(
        Campaign.campaign_id == campaign_uuid,
        Campaign.user_id == user.public_id,
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return str(campaign_uuid)


def _safe_filename(filename: str | None) -> str:
    cleaned = Path(filename or "uploaded-document").name.strip()
    return cleaned or "uploaded-document"
