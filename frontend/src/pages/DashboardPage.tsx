import { useEffect, useMemo, useState } from "react";
import { Download, RefreshCw, ShieldCheck } from "lucide-react";

import {
  ApiError,
  approveDocument,
  exportCsvUrl,
  listDocuments,
  updateDocument,
  uploadDocument
} from "../api/client";
import { DocumentTable } from "../components/DocumentTable";
import { EditableDocumentForm } from "../components/EditableDocumentForm";
import { UploadDropzone } from "../components/UploadDropzone";
import type { DocumentRecord, DocumentUpdate } from "../types/document";

export function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentRecord | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  async function refreshDocuments(selectId?: number) {
    setIsLoading(true);
    try {
      const nextDocuments = await listDocuments();
      setDocuments(nextDocuments);
      if (selectId) {
        setSelectedDocument(nextDocuments.find((item) => item.id === selectId) ?? null);
      } else if (selectedDocument) {
        setSelectedDocument(
          nextDocuments.find((item) => item.id === selectedDocument.id) ?? null
        );
      }
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Kunne ikke hente bilag.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshDocuments();
  }, []);

  async function handleUpload(file: File) {
    setError(null);
    setMessage(null);
    setIsUploading(true);
    try {
      const uploaded = await uploadDocument(file);
      setSelectedDocument(uploaded);
      await refreshDocuments(uploaded.id);
      if (uploaded.status === "failed") {
        setError(
          uploaded.error_message ??
            "Automatisk analyse feilet. Se backend-terminalen for detaljer."
        );
      } else if (uploaded.confidence_status === "OK") {
        setMessage("Bilaget er analysert og klart for kontroll.");
      } else {
        setMessage("Bilaget er analysert, men må sjekkes før godkjenning.");
      }
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Opplasting feilet.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleSave(documentId: number, payload: DocumentUpdate) {
    setError(null);
    setMessage(null);
    setIsSaving(true);
    try {
      const updated = await updateDocument(documentId, payload);
      setSelectedDocument(updated);
      await refreshDocuments(updated.id);
      setMessage("Endringene er lagret.");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Kunne ikke lagre.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleApprove(documentId: number) {
    setError(null);
    setMessage(null);
    setIsApproving(true);
    try {
      const approved = await approveDocument(documentId);
      setSelectedDocument(approved);
      await refreshDocuments(approved.id);
      setMessage("Bilaget er godkjent og blir med i CSV-eksporten.");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Kunne ikke godkjenne.");
    } finally {
      setIsApproving(false);
    }
  }

  const approvedDocuments = useMemo(
    () => documents.filter((document) => document.status === "approved"),
    [documents]
  );
  const reviewCount = documents.filter((document) =>
    ["needs_review", "failed", "extracted"].includes(document.status)
  ).length;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>Bilagspilot</h1>
          <p>AI-basert bilagsassistent for små håndverksbedrifter</p>
        </div>
        <div className="topbar-actions">
          <button className="button secondary" type="button" onClick={() => refreshDocuments()}>
            <RefreshCw size={17} />
            Oppdater
          </button>
          <a className="button primary" href={exportCsvUrl()}>
            <Download size={17} />
            Eksporter CSV
          </a>
        </div>
      </header>

      <section className="metrics-band" aria-label="Nøkkeltall">
        <div>
          <span>Til kontroll</span>
          <strong>{reviewCount}</strong>
        </div>
        <div>
          <span>Godkjent</span>
          <strong>{approvedDocuments.length}</strong>
        </div>
        <div>
          <span>Totalt</span>
          <strong>{documents.length}</strong>
        </div>
        <div className="trust-note">
          <ShieldCheck size={19} />
          <span>AI foreslår. Du kontrollerer.</span>
        </div>
      </section>

      {message ? <div className="alert success-alert">{message}</div> : null}
      {error ? <div className="alert danger-alert">{error}</div> : null}

      <div className="workspace-grid">
        <div className="left-column">
          <UploadDropzone isUploading={isUploading} onUpload={handleUpload} />
          <section className="history-section">
            <div className="section-heading">
              <div>
                <h2>Historikk</h2>
                <p>{isLoading ? "Laster bilag..." : "Velg et bilag for kontroll."}</p>
              </div>
            </div>
            <DocumentTable
              documents={documents}
              selectedId={selectedDocument?.id}
              onSelect={setSelectedDocument}
            />
          </section>
        </div>

        <EditableDocumentForm
          document={selectedDocument}
          isSaving={isSaving}
          isApproving={isApproving}
          onSave={handleSave}
          onApprove={handleApprove}
        />
      </div>

      <section className="approved-section">
        <div className="section-heading">
          <div>
            <h2>Godkjente bilag</h2>
            <p>Disse radene blir med i CSV-eksporten.</p>
          </div>
        </div>
        <DocumentTable
          documents={approvedDocuments}
          selectedId={selectedDocument?.id}
          onSelect={setSelectedDocument}
        />
      </section>
    </main>
  );
}
