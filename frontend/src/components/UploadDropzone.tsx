import { ChangeEvent, DragEvent, useRef, useState } from "react";
import { FileUp, Loader2 } from "lucide-react";

type UploadDropzoneProps = {
  isUploading: boolean;
  onUpload: (file: File) => void;
};

export function UploadDropzone({ isUploading, onUpload }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFile(file?: File) {
    if (file) {
      onUpload(file);
    }
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    handleFile(event.target.files?.[0]);
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    handleFile(event.dataTransfer.files?.[0]);
  }

  return (
    <section
      className={`upload-zone ${isDragging ? "dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <div className="upload-icon" aria-hidden="true">
        {isUploading ? <Loader2 className="spin" size={24} /> : <FileUp size={24} />}
      </div>
      <div>
        <h2>Last opp bilag</h2>
        <p>PDF, PNG eller JPG. Filen analyseres før du godkjenner noe.</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        onChange={handleInputChange}
        hidden
      />
      <button
        className="button primary"
        type="button"
        disabled={isUploading}
        onClick={() => inputRef.current?.click()}
      >
        <FileUp size={17} />
        Velg fil
      </button>
    </section>
  );
}

