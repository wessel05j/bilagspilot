from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings


ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


class FileStorageError(ValueError):
    pass


@dataclass(frozen=True)
class StoredFile:
    path: Path
    stored_filename: str
    mime_type: str
    size_bytes: int


def detect_file_type(filename: str | None) -> tuple[str, str]:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise FileStorageError(f"Filtypen støttes ikke. Bruk {allowed}.")
    return suffix, ALLOWED_EXTENSIONS[suffix]


async def save_upload_file(upload_file: UploadFile) -> StoredFile:
    suffix, mime_type = detect_file_type(upload_file.filename)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}{suffix}"
    target_path = settings.upload_dir / stored_filename
    size_bytes = 0

    try:
        with target_path.open("wb") as buffer:
            while chunk := await upload_file.read(1024 * 1024):
                size_bytes += len(chunk)
                if size_bytes > settings.max_upload_bytes:
                    raise FileStorageError("Filen er for stor. Maks størrelse er 10 MB.")
                buffer.write(chunk)
    except Exception:
        target_path.unlink(missing_ok=True)
        raise

    if size_bytes == 0:
        target_path.unlink(missing_ok=True)
        raise FileStorageError("Filen er tom.")

    return StoredFile(
        path=target_path,
        stored_filename=stored_filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
    )

