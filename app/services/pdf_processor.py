"""
PDF Processor Service

Extracts text and tables from PDF documents.
"""

import io
from typing import List, Optional
from dataclasses import dataclass, field
import pdfplumber


@dataclass
class PDFPage:
    """Represents a single PDF page."""
    page_number: int
    text_content: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    title: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'page_number': self.page_number,
            'title': self.title,
            'text_content': self.text_content,
            'tables': self.tables,
        }


@dataclass
class ProcessedPDF:
    """Represents a processed PDF document."""
    filename: str
    total_pages: int
    pages: List[PDFPage] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'filename': self.filename,
            'total_pages': self.total_pages,
            'pages': [p.to_dict() for p in self.pages],
        }


class PDFProcessor:
    """Processes PDF files and extracts content."""

    def process_uploaded_file(self, uploaded_file) -> ProcessedPDF:
        """Process an uploaded PDF file."""
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        return self.process_bytes(file_bytes, uploaded_file.name)

    def process_bytes(self, file_bytes: bytes, filename: str) -> ProcessedPDF:
        """Process PDF from bytes."""
        pages = []

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            total_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                page_num = i + 1

                # Extract text
                text = page.extract_text() or ""
                text_lines = [line.strip() for line in text.split('\n') if line.strip()]

                # Try to get title from first significant line
                title = None
                for line in text_lines[:3]:
                    if len(line) > 5 and len(line) < 100:
                        title = line
                        break

                # Extract tables
                tables = []
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        # Convert table to markdown-like format
                        table_str = self._table_to_string(table)
                        if table_str:
                            tables.append(table_str)

                pdf_page = PDFPage(
                    page_number=page_num,
                    text_content=text_lines,
                    tables=tables,
                    title=title or f"Page {page_num}"
                )
                pages.append(pdf_page)

        return ProcessedPDF(
            filename=filename,
            total_pages=total_pages,
            pages=pages
        )

    def _table_to_string(self, table: List[List]) -> str:
        """Convert a table to a string representation."""
        if not table:
            return ""

        rows = []
        for row in table:
            cells = [str(cell or "").strip() for cell in row]
            if any(cells):  # Only include non-empty rows
                rows.append(" | ".join(cells))

        return "\n".join(rows)


def create_page_embedding_content(page_dict: dict) -> str:
    """Create embedding content from a PDF page dictionary."""
    parts = []

    if page_dict.get('title'):
        parts.append(f"Title: {page_dict['title']}")

    parts.append(f"Page: {page_dict.get('page_number', '?')}")

    if page_dict.get('text_content'):
        parts.append("Content: " + " ".join(page_dict['text_content']))

    if page_dict.get('tables'):
        for i, table in enumerate(page_dict['tables'], 1):
            parts.append(f"Table {i}: {table}")

    return "\n".join(parts)
