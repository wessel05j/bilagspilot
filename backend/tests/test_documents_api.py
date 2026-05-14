from app.services.openai_extraction import ReceiptExtraction


def fake_extraction() -> ReceiptExtraction:
    return ReceiptExtraction(
        supplier_name="Byggmakker Gjøvik",
        invoice_date="2026-05-14",
        total_amount=1249.0,
        vat_amount=249.8,
        currency="NOK",
        invoice_number="12345",
        category="materialer",
        missing_fields=[],
        notes="MVA og totalbeløp ble funnet tydelig.",
    )


def test_upload_extracts_document(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.uploads.extract_document_fields",
        lambda *_args, **_kwargs: fake_extraction(),
    )

    response = client.post(
        "/api/uploads",
        files={"file": ("fake-bilag.jpg", b"fake image bytes", "image/jpeg")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["supplier_name"] == "Byggmakker Gjøvik"
    assert body["invoice_date"] == "2026-05-14"
    assert body["total_amount"] == 1249.0
    assert body["confidence_status"] == "OK"
    assert body["status"] == "extracted"


def test_update_approve_and_export_csv(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.uploads.extract_document_fields",
        lambda *_args, **_kwargs: fake_extraction(),
    )

    upload_response = client.post(
        "/api/uploads",
        files={"file": ("fake-bilag.png", b"fake image bytes", "image/png")},
    )
    document_id = upload_response.json()["id"]

    update_response = client.patch(
        f"/api/documents/{document_id}",
        json={"category": "verktøy", "review_notes": "Kontrollert manuelt."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["category"] == "verktøy"

    approve_response = client.post(f"/api/documents/{document_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    export_response = client.get("/api/exports/csv")
    assert export_response.status_code == 200
    assert "Byggmakker Gjøvik" in export_response.text
    assert "verktøy" in export_response.text


def test_rejects_unsupported_upload_type(client):
    response = client.post(
        "/api/uploads",
        files={"file": ("notes.txt", b"not a receipt", "text/plain")},
    )

    assert response.status_code == 400
    assert "Filtypen støttes ikke" in response.json()["detail"]


def test_cannot_approve_document_with_missing_required_fields(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.uploads.extract_document_fields",
        lambda *_args, **_kwargs: ReceiptExtraction(
            supplier_name=None,
            invoice_date=None,
            total_amount=None,
            vat_amount=None,
            currency=None,
            invoice_number=None,
            category=None,
            missing_fields=["supplier_name", "invoice_date", "total_amount", "currency"],
            notes="Uklart bilag.",
        ),
    )

    upload_response = client.post(
        "/api/uploads",
        files={"file": ("unclear.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    document_id = upload_response.json()["id"]

    approve_response = client.post(f"/api/documents/{document_id}/approve")
    assert approve_response.status_code == 400
    assert "Kan ikke godkjenne" in approve_response.json()["detail"]

