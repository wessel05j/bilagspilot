import { Eye } from "lucide-react";

import type { DocumentRecord } from "../types/document";
import { formatMoney, statusLabel } from "../utils/status";
import { StatusBadge } from "./StatusBadge";

type DocumentTableProps = {
  documents: DocumentRecord[];
  selectedId?: number;
  onSelect: (document: DocumentRecord) => void;
};

export function DocumentTable({
  documents,
  selectedId,
  onSelect
}: DocumentTableProps) {
  if (documents.length === 0) {
    return <p className="empty-table">Ingen bilag er registrert ennå.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Bilag</th>
            <th>Dato</th>
            <th>Leverandør</th>
            <th>Beløp</th>
            <th>Kategori</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => (
            <tr key={document.id} className={selectedId === document.id ? "selected" : ""}>
              <td title={document.original_filename}>{document.original_filename}</td>
              <td>{document.invoice_date ?? "-"}</td>
              <td title={document.supplier_name ?? undefined}>
                {document.supplier_name ?? "-"}
              </td>
              <td>{formatMoney(document.total_amount, document.currency)}</td>
              <td>{document.category ?? "-"}</td>
              <td>
                <StatusBadge value={statusLabel(document.status)} />
              </td>
              <td className="align-right">
                <button
                  className="icon-button"
                  type="button"
                  title="Åpne for kontroll"
                  onClick={() => onSelect(document)}
                >
                  <Eye size={17} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
