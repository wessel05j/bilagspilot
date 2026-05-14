from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    id: int
    original_filename: str
    file_type: str
    supplier_name: str | None = None
    invoice_date: date | None = None
    total_amount: float | None = None
    vat_amount: float | None = None
    currency: str | None = None
    invoice_number: str | None = None
    category: str | None = None
    confidence_status: str
    review_notes: str | None = None
    status: str
    raw_ai_response: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    supplier_name: str | None = Field(default=None, max_length=255)
    invoice_date: date | None = None
    total_amount: float | None = Field(default=None, ge=0)
    vat_amount: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    invoice_number: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    confidence_status: str | None = Field(default=None, max_length=30)
    review_notes: str | None = None


class ErrorResponse(BaseModel):
    detail: str

