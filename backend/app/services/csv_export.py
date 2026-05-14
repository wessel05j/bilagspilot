import csv
from io import StringIO
from typing import Iterable

from app.models import Document


CSV_FIELDS = [
    "id",
    "supplier_name",
    "invoice_date",
    "total_amount",
    "vat_amount",
    "currency",
    "invoice_number",
    "category",
    "review_notes",
]


def _format_amount(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def documents_to_csv(documents: Iterable[Document]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()

    for document in documents:
        writer.writerow(
            {
                "id": document.id,
                "supplier_name": document.supplier_name or "",
                "invoice_date": document.invoice_date.isoformat()
                if document.invoice_date
                else "",
                "total_amount": _format_amount(document.total_amount),
                "vat_amount": _format_amount(document.vat_amount),
                "currency": document.currency or "",
                "invoice_number": document.invoice_number or "",
                "category": document.category or "",
                "review_notes": document.review_notes or "",
            }
        )

    return "\ufeff" + output.getvalue()

