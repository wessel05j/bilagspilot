from app.services.validation import validate_extraction


def test_validate_extraction_accepts_common_norwegian_date_and_decimal_formats():
    result = validate_extraction(
        {
            "supplier_name": "Circle K",
            "invoice_date": "14.05.2026",
            "total_amount": "1 249,00",
            "vat_amount": "249,80",
            "currency": "nok",
            "invoice_number": "K123",
            "category": "drivstoff",
            "missing_fields": [],
            "notes": "Tydelig kvittering.",
        }
    )

    assert result.fields["invoice_date"].isoformat() == "2026-05-14"
    assert result.fields["total_amount"] == 1249.0
    assert result.fields["vat_amount"] == 249.8
    assert result.fields["currency"] == "NOK"
    assert result.confidence_status == "OK"
    assert result.document_status == "extracted"


def test_validate_extraction_marks_missing_required_fields():
    result = validate_extraction(
        {
            "supplier_name": "",
            "invoice_date": "ukjent",
            "total_amount": None,
            "currency": None,
            "category": "ukjent",
            "missing_fields": [],
        }
    )

    assert result.fields["category"] == "annet"
    assert result.confidence_status == "Mangler data"
    assert result.document_status == "needs_review"
    assert "supplier_name" in result.missing_fields
    assert "invoice_date" in result.missing_fields
    assert "total_amount" in result.missing_fields
    assert "currency" in result.missing_fields
