import type { DocumentRecord, DocumentUpdate } from "../types/document";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    let message = "Noe gikk galt mot API-et.";
    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message);
  }
  return (await response.json()) as T;
}

export async function listDocuments(): Promise<DocumentRecord[]> {
  return request<DocumentRecord[]>("/api/documents");
}

export async function uploadDocument(file: File): Promise<DocumentRecord> {
  const formData = new FormData();
  formData.append("file", file);
  return request<DocumentRecord>("/api/uploads", {
    method: "POST",
    body: formData
  });
}

export async function updateDocument(
  documentId: number,
  payload: DocumentUpdate
): Promise<DocumentRecord> {
  return request<DocumentRecord>(`/api/documents/${documentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function approveDocument(
  documentId: number
): Promise<DocumentRecord> {
  return request<DocumentRecord>(`/api/documents/${documentId}/approve`, {
    method: "POST"
  });
}

export async function deleteDocument(documentId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: "DELETE"
  });

  if (!response.ok) {
    let message = "Kunne ikke slette bilaget.";
    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message);
  }
}

export function exportCsvUrl(): string {
  return `${API_BASE_URL}/api/exports/csv`;
}
