import base64
from pathlib import Path
from typing import Literal

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

from app.config import is_openai_configured, settings


Category = Literal[
    "materialer",
    "verktøy",
    "drivstoff",
    "parkering",
    "telefon",
    "annet",
]


class ReceiptExtraction(BaseModel):
    supplier_name: str | None = None
    invoice_date: str | None = Field(
        default=None, description="Dato i ISO-format YYYY-MM-DD når mulig."
    )
    total_amount: float | None = None
    vat_amount: float | None = None
    currency: str | None = None
    invoice_number: str | None = None
    category: Category | None = None
    missing_fields: list[str] = Field(default_factory=list)
    notes: str | None = None


class ExtractionServiceError(RuntimeError):
    pass


SYSTEM_PROMPT = """
Du leser norske og engelske fakturaer eller kvitteringer for en liten
håndverkerbedrift. Returner bare strukturerte felt. Ikke gjett når feltet
ikke er tydelig. Sett uklare eller manglende felt til null og legg feltnavnet
i missing_fields. Beløp skal være tall, ikke tekst. Foreslå én kategori blant:
materialer, verktøy, drivstoff, parkering, telefon, annet.
""".strip()


def _encode_file(file_path: Path) -> str:
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")


def _build_file_content(file_path: Path, mime_type: str) -> dict[str, str]:
    encoded = _encode_file(file_path)
    if mime_type == "application/pdf":
        return {
            "type": "input_file",
            "filename": file_path.name,
            "file_data": f"data:application/pdf;base64,{encoded}",
        }

    return {
        "type": "input_image",
        "image_url": f"data:{mime_type};base64,{encoded}",
    }


def extract_document_fields(file_path: Path, mime_type: str) -> ReceiptExtraction:
    if not is_openai_configured():
        raise ExtractionServiceError(
            "OPENAI_API_KEY mangler eller er placeholder i backend/.env. "
            "Legg inn nøkkelen og restart backend."
        )

    client = OpenAI(api_key=(settings.openai_api_key or "").strip())

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        _build_file_content(file_path, mime_type),
                        {
                            "type": "input_text",
                            "text": "Hent ut nøkkelfeltene fra dette bilaget.",
                        },
                    ],
                },
            ],
            text_format=ReceiptExtraction,
        )
    except OpenAIError as exc:
        raise ExtractionServiceError(f"OpenAI-kallet feilet: {exc}") from exc
    except Exception as exc:
        raise ExtractionServiceError(f"Kunne ikke analysere bilaget: {exc}") from exc

    if response.output_parsed is None:
        raise ExtractionServiceError("OpenAI returnerte ikke strukturert JSON.")

    return response.output_parsed
