from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


ESSENTIAL_FIELDS = ["supplier_name", "invoice_date", "total_amount", "currency"]
ALLOWED_CATEGORIES = {
    "materialer",
    "verktøy",
    "drivstoff",
    "parkering",
    "telefon",
    "annet",
}


@dataclass(frozen=True)
class ValidatedExtraction:
    fields: dict[str, Any]
    confidence_status: str
    document_status: str
    review_notes: str | None
    missing_fields: list[str]


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_amount(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, int | float):
        return round(float(value), 2) if value >= 0 else None

    text = str(value).strip().replace(" ", "").replace(",", ".")
    try:
        amount = float(text)
    except ValueError:
        return None
    return round(amount, 2) if amount >= 0 else None


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value

    text = str(value).strip()
    for date_format in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    return None


def _append_missing(missing_fields: list[str], field_name: str) -> None:
    if field_name not in missing_fields:
        missing_fields.append(field_name)


def validate_extraction(data: dict[str, Any]) -> ValidatedExtraction:
    missing_fields = list(data.get("missing_fields") or [])

    category = _clean_text(data.get("category"))
    if category not in ALLOWED_CATEGORIES:
        category = "annet" if category else None

    fields: dict[str, Any] = {
        "supplier_name": _clean_text(data.get("supplier_name")),
        "invoice_date": _parse_date(data.get("invoice_date")),
        "total_amount": _parse_amount(data.get("total_amount")),
        "vat_amount": _parse_amount(data.get("vat_amount")),
        "currency": (_clean_text(data.get("currency")) or "").upper() or None,
        "invoice_number": _clean_text(data.get("invoice_number")),
        "category": category,
    }

    for field_name in ESSENTIAL_FIELDS:
        if fields[field_name] is None:
            _append_missing(missing_fields, field_name)

    notes = _clean_text(data.get("notes"))
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        notes = f"{notes} Mangler: {missing_text}." if notes else f"Mangler: {missing_text}."

    if any(field in missing_fields for field in ESSENTIAL_FIELDS):
        confidence_status = "Mangler data"
        document_status = "needs_review"
    elif missing_fields:
        confidence_status = "Må sjekkes"
        document_status = "needs_review"
    else:
        confidence_status = "OK"
        document_status = "extracted"

    return ValidatedExtraction(
        fields=fields,
        confidence_status=confidence_status,
        document_status=document_status,
        review_notes=notes,
        missing_fields=missing_fields,
    )


def required_fields_missing(document: Any) -> list[str]:
    missing: list[str] = []
    for field_name in ESSENTIAL_FIELDS:
        if getattr(document, field_name, None) in (None, ""):
            missing.append(field_name)
    return missing

