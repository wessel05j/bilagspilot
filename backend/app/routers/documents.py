from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentRead, DocumentUpdate
from app.services.validation import required_fields_missing

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _get_document_or_404(document_id: int, db: Session) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Bilaget finnes ikke.")
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[Document]:
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
    return query.order_by(Document.created_at.desc(), Document.id.desc()).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    return _get_document_or_404(document_id, db)


@router.patch("/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
) -> Document:
    document = _get_document_or_404(document_id, db)
    update_data = payload.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(document, field_name, value)

    if document.status in {"failed", "needs_review"}:
        document.status = "needs_review"

    db.commit()
    db.refresh(document)
    return document


@router.post("/{document_id}/approve", response_model=DocumentRead)
def approve_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = _get_document_or_404(document_id, db)
    missing_fields = required_fields_missing(document)
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise HTTPException(
            status_code=400,
            detail=f"Kan ikke godkjenne før disse feltene er fylt ut: {missing}.",
        )

    document.status = "approved"
    document.confidence_status = "OK"
    db.commit()
    db.refresh(document)
    return document

