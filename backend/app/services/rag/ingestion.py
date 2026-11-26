from typing import List, Dict, Any, Optional
import os
import hashlib
import re
from app.core.logging import logger
from app.core.exceptions import IngestionException
from app.services.rag.retrieval import vector_store

try:
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz  # PyMuPDF fallback
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF (pymupdf) is not installed. PDF ingestion will rely on fallback text extraction.")


class DocumentIngestionService:
    """
    Parses supplier documents (PDFs, contracts, delivery slips, notices),
    extracts structured sections, generates overlapping semantic chunks,
    and indexes them into the Qdrant vector database.
    """

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from each page of a PDF file.
        Returns a list of dicts with 'page_number' and 'text'.
        """
        if not os.path.exists(file_path):
            raise IngestionException(f"File not found: {file_path}")

        pages_data = []

        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    text = page.get_text("text")
                    # Clean up extraneous whitespace
                    clean_text = re.sub(r"\s+", " ", text).strip()
                    if clean_text:
                        pages_data.append({
                            "page_number": page_idx + 1,
                            "text": clean_text
                        })
                doc.close()
                return pages_data
            except Exception as e:
                logger.error(f"Error parsing PDF with PyMuPDF: {e}")

        # Fallback text loader for .txt or unparsed formats
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            clean_text = re.sub(r"\s+", " ", content).strip()
            pages_data.append({"page_number": 1, "text": clean_text})
        except Exception as e:
            raise IngestionException(f"Failed to read file contents: {e}")

        return pages_data

    def chunk_text(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Splits text into overlapping chunks respecting sentence boundaries where possible.
        """
        chunks = []
        if not text:
            return chunks

        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        chunk_idx = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "page_number": page_number,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1
                    # Keep overlap from end of current_chunk
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + " " + sentence
                else:
                    # Single sentence longer than chunk_size, hard slice
                    for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
                        slice_text = sentence[i:i + self.chunk_size]
                        chunks.append({
                            "content": slice_text.strip(),
                            "page_number": page_number,
                            "chunk_index": chunk_idx
                        })
                        chunk_idx += 1
                    current_chunk = ""

        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "page_number": page_number,
                "chunk_index": chunk_idx
            })

        return chunks

    def ingest_document(
        self,
        file_path: str,
        doc_id: str,
        title: str,
        supplier_id: Optional[str] = None,
        supplier_name: Optional[str] = None,
        doc_type: str = "contract"
    ) -> Dict[str, Any]:
        """
        End-to-end ingestion: extract -> chunk -> embed -> upsert to Qdrant.
        """
        pages = self.extract_text_from_pdf(file_path)
        all_chunks = []
        global_chunk_idx = 0

        for page in pages:
            page_chunks = self.chunk_text(page["text"], page["page_number"])
            for pc in page_chunks:
                all_chunks.append({
                    "doc_id": doc_id,
                    "doc_title": title,
                    "supplier_id": supplier_id,
                    "supplier_name": supplier_name or "Unknown Supplier",
                    "doc_type": doc_type,
                    "page_number": pc["page_number"],
                    "chunk_index": global_chunk_idx,
                    "content": pc["content"]
                })
                global_chunk_idx += 1

        upserted_count = vector_store.upsert_chunks(all_chunks)
        file_hash = self.compute_file_hash(file_path)
        file_size = os.path.getsize(file_path)

        logger.info(f"Ingested document '{title}' ({doc_id}): {len(all_chunks)} chunks indexed into Qdrant.")

        return {
            "doc_id": doc_id,
            "title": title,
            "chunk_count": len(all_chunks),
            "file_hash": file_hash,
            "file_size": file_size,
            "upserted_count": upserted_count
        }


ingestion_service = DocumentIngestionService()
