"""Extract raw text from uploaded PDF, DOCX, and TXT files."""

from pathlib import Path

import docx
from pypdf import PdfReader

from app.utils.exceptions import FileProcessingError


def extract_text(file_path: str, content_type: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if suffix == ".pdf":
            return _extract_pdf(path)
        if suffix == ".docx":
            return _extract_docx(path)
        if suffix == ".txt":
            return _extract_txt(path)
    except Exception as exc:  # noqa: BLE001
        raise FileProcessingError(f"Failed to extract text from '{path.name}': {exc}") from exc

    raise FileProcessingError(f"Unsupported file type for extraction: {suffix}")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(path: Path) -> str:
    document = docx.Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")
