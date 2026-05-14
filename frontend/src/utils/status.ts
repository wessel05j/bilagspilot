import type { DocumentRecord } from "../types/document";

export function statusLabel(status: DocumentRecord["status"]): string {
  const labels: Record<DocumentRecord["status"], string> = {
    uploaded: "Ny",
    extracted: "Klar",
    needs_review: "Sjekk",
    approved: "Godkjent",
    failed: "Feilet"
  };
  return labels[status];
}

export function statusTone(status: string): string {
  if (
    status === "OK" ||
    status === "approved" ||
    status === "extracted" ||
    status === "Godkjent" ||
    status === "Klar"
  ) {
    return "success";
  }
  if (status === "Mangler data" || status === "failed" || status === "Feilet") {
    return "danger";
  }
  if (status === "Må sjekkes" || status === "Sjekk" || status === "needs_review") {
    return "warning";
  }
  return "neutral";
}

export function formatMoney(amount: number | null, currency?: string | null): string {
  if (amount === null) {
    return "-";
  }
  return new Intl.NumberFormat("no-NO", {
    style: "currency",
    currency: currency || "NOK"
  }).format(amount);
}
