import { FormEvent, useEffect, useState } from "react";
import { Check, Save } from "lucide-react";

import type { DocumentRecord, DocumentUpdate } from "../types/document";
import { StatusBadge } from "./StatusBadge";

const CATEGORIES = [
  "materialer",
  "verktøy",
  "drivstoff",
  "parkering",
  "telefon",
  "annet"
];

type EditableDocumentFormProps = {
  document: DocumentRecord | null;
  isSaving: boolean;
  isApproving: boolean;
  onSave: (documentId: number, payload: DocumentUpdate) => void;
  onApprove: (documentId: number) => void;
};

type FormState = {
  supplier_name: string;
  invoice_date: string;
  total_amount: string;
  vat_amount: string;
  currency: string;
  invoice_number: string;
  category: string;
  review_notes: string;
};

function toFormState(document: DocumentRecord): FormState {
  return {
    supplier_name: document.supplier_name ?? "",
    invoice_date: document.invoice_date ?? "",
    total_amount: document.total_amount?.toString() ?? "",
    vat_amount: document.vat_amount?.toString() ?? "",
    currency: document.currency ?? "NOK",
    invoice_number: document.invoice_number ?? "",
    category: document.category ?? "annet",
    review_notes: document.review_notes ?? ""
  };
}

export function EditableDocumentForm({
  document,
  isSaving,
  isApproving,
  onSave,
  onApprove
}: EditableDocumentFormProps) {
  const [formState, setFormState] = useState<FormState | null>(null);

  useEffect(() => {
    setFormState(document ? toFormState(document) : null);
  }, [document]);

  if (!document || !formState) {
    return (
      <section className="review-empty">
        <h2>Ingen bilag valgt</h2>
        <p>Last opp et bilag eller velg ett fra historikken for å kontrollere feltene.</p>
      </section>
    );
  }

  const activeDocument = document;
  const activeFormState = formState;

  function updateField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setFormState((current) => (current ? { ...current, [field]: value } : current));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: DocumentUpdate = {
      supplier_name: activeFormState.supplier_name.trim() || null,
      invoice_date: activeFormState.invoice_date || null,
      total_amount: activeFormState.total_amount
        ? Number(activeFormState.total_amount)
        : null,
      vat_amount: activeFormState.vat_amount ? Number(activeFormState.vat_amount) : null,
      currency: activeFormState.currency.trim().toUpperCase() || null,
      invoice_number: activeFormState.invoice_number.trim() || null,
      category: activeFormState.category || null,
      review_notes: activeFormState.review_notes.trim() || null
    };
    onSave(activeDocument.id, payload);
  }

  return (
    <section className="review-panel">
      <div className="section-heading">
        <div>
          <h2>Kontroller bilag</h2>
          <p>{activeDocument.original_filename}</p>
        </div>
        <div className="status-stack">
          <StatusBadge value={activeDocument.confidence_status} />
          <StatusBadge value={activeDocument.status} />
        </div>
      </div>

      {activeDocument.error_message ? (
        <div className="alert danger-alert">{activeDocument.error_message}</div>
      ) : null}

      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Leverandør
          <input
            value={formState.supplier_name}
            onChange={(event) => updateField("supplier_name", event.target.value)}
          />
        </label>
        <label>
          Dato
          <input
            type="date"
            value={formState.invoice_date}
            onChange={(event) => updateField("invoice_date", event.target.value)}
          />
        </label>
        <label>
          Totalbeløp
          <input
            min="0"
            step="0.01"
            type="number"
            value={formState.total_amount}
            onChange={(event) => updateField("total_amount", event.target.value)}
          />
        </label>
        <label>
          MVA-beløp
          <input
            min="0"
            step="0.01"
            type="number"
            value={formState.vat_amount}
            onChange={(event) => updateField("vat_amount", event.target.value)}
          />
        </label>
        <label>
          Valuta
          <input
            value={formState.currency}
            onChange={(event) => updateField("currency", event.target.value)}
          />
        </label>
        <label>
          Faktura/kvittering nr.
          <input
            value={formState.invoice_number}
            onChange={(event) => updateField("invoice_number", event.target.value)}
          />
        </label>
        <label>
          Kategori
          <select
            value={formState.category}
            onChange={(event) => updateField("category", event.target.value)}
          >
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>
        <label className="wide">
          Kontrollnotat
          <textarea
            rows={3}
            value={formState.review_notes}
            onChange={(event) => updateField("review_notes", event.target.value)}
          />
        </label>
        <div className="form-actions">
          <button className="button secondary" type="submit" disabled={isSaving}>
            <Save size={17} />
            Lagre
          </button>
          <button
            className="button primary"
            type="button"
            disabled={isApproving || activeDocument.status === "approved"}
            onClick={() => onApprove(activeDocument.id)}
          >
            <Check size={17} />
            Godkjenn
          </button>
        </div>
      </form>
    </section>
  );
}
