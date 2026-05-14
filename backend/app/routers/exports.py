from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.services.csv_export import documents_to_csv

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/csv")
def export_approved_documents(db: Session = Depends(get_db)) -> Response:
    documents = (
        db.query(Document)
        .filter(Document.status == "approved")
        .order_by(Document.invoice_date.desc(), Document.id.desc())
        .all()
    )
    csv_content = documents_to_csv(documents)
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bilagspilot-export.csv"},
    )

