import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentRead
from app.services.file_storage import FileStorageError, save_upload_file
from app.services.openai_extraction import (
    ExtractionServiceError,
    extract_document_fields,
)
from app.services.validation import validate_extraction

router = APIRouter(prefix="/api/uploads", tags=["uploads"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Ugyldig fil"}},
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Document:
    try:
        stored_file = await save_upload_file(file)
    except FileStorageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        original_filename=file.filename or "ukjent-fil",
        stored_filename=stored_file.stored_filename,
        file_type=stored_file.mime_type,
        status="uploaded",
        confidence_status="Mangler data",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        extraction = extract_document_fields(stored_file.path, stored_file.mime_type)
        validated = validate_extraction(extraction.model_dump())
        for field_name, value in validated.fields.items():
            setattr(document, field_name, value)
        document.confidence_status = validated.confidence_status
        document.status = validated.document_status
        document.review_notes = validated.review_notes
        document.raw_ai_response = extraction.model_dump_json(indent=2)
    except ExtractionServiceError as exc:
        document.status = "failed"
        document.confidence_status = "Må sjekkes"
        document.review_notes = "Automatisk analyse feilet. Prøv igjen eller legg inn data manuelt."
        document.error_message = str(exc)
        logger.warning(
            "AI extraction failed for document_id=%s filename=%s: %s",
            document.id,
            document.original_filename,
            exc,
        )

    db.commit()
    db.refresh(document)
    return document
