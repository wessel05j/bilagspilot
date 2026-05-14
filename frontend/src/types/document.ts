export type DocumentStatus =
  | "uploaded"
  | "extracted"
  | "needs_review"
  | "approved"
  | "failed";

export type ConfidenceStatus = "OK" | "Må sjekkes" | "Mangler data";

export type DocumentRecord = {
  id: number;
  original_filename: string;
  file_type: string;
  supplier_name: string | null;
  invoice_date: string | null;
  total_amount: number | null;
  vat_amount: number | null;
  currency: string | null;
  invoice_number: string | null;
  category: string | null;
  confidence_status: ConfidenceStatus | string;
  review_notes: string | null;
  status: DocumentStatus;
  raw_ai_response: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentUpdate = Partial<
  Pick<
    DocumentRecord,
    | "supplier_name"
    | "invoice_date"
    | "total_amount"
    | "vat_amount"
    | "currency"
    | "invoice_number"
    | "category"
    | "confidence_status"
    | "review_notes"
  >
>;

