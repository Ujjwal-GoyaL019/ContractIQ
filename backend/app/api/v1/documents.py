from typing import List, Optional
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.db.models.document import SupplierDocument
from app.db.models.supplier import Supplier
from app.schemas.rag import DocumentMetadata
from app.services.rag.ingestion import ingestion_service
from app.core.exceptions import EntityNotFoundException, IngestionException

router = APIRouter(prefix="/documents", tags=["Supplier Documents"])

from app.core.security import validate_and_save_upload

DOCS_STORAGE_DIR = os.path.join(os.getcwd(), "data", "supplier_docs")
os.makedirs(DOCS_STORAGE_DIR, exist_ok=True)


@router.get("", response_model=List[DocumentMetadata])
def get_documents(
    supplier_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(SupplierDocument)
    if supplier_id:
        query = query.filter(SupplierDocument.supplier_id == supplier_id)
    if doc_type:
        query = query.filter(SupplierDocument.doc_type == doc_type)

    docs = query.offset(skip).limit(limit).all()
    results = []
    for d in docs:
        results.append(
            DocumentMetadata(
                id=d.id,
                title=d.title,
                filename=d.filename,
                doc_type=d.doc_type,
                supplier_id=d.supplier_id,
                supplier_name=d.supplier.name if d.supplier else None,
                chunk_count=d.chunk_count,
                file_size_bytes=d.file_size_bytes,
                created_at=d.created_at,
                summary=d.summary
            )
        )
    return results


@router.post("/upload", response_model=DocumentMetadata, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form("contract"),
    supplier_id: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate supplier if provided
    supplier_name = None
    if supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            raise EntityNotFoundException("Supplier", supplier_id)
        supplier_name = supplier.name

    # Secure file validation, size limits (15MB), magic byte verification, and path traversal prevention
    prefix_id = supplier_id or "general"
    safe_filename, file_path, file_size = await validate_and_save_upload(
        upload_file=file,
        destination_dir=DOCS_STORAGE_DIR,
        prefix_id=prefix_id
    )

    # Ingest document chunks into Qdrant vector store
    import uuid
    doc_id = str(uuid.uuid4())

    ingest_result = ingestion_service.ingest_document(
        file_path=file_path,
        doc_id=doc_id,
        title=title,
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        doc_type=doc_type
    )

    # Save record to relational database
    doc_record = SupplierDocument(
        id=doc_id,
        title=title,
        filename=file.filename,
        file_path=file_path,
        doc_type=doc_type,
        supplier_id=supplier_id,
        file_size_bytes=ingest_result["file_size"],
        chunk_count=ingest_result["chunk_count"],
        content_hash=ingest_result["file_hash"],
        summary=summary or f"Document '{title}' covering terms and operational clauses for {supplier_name or 'general supplier'}."
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return DocumentMetadata(
        id=doc_record.id,
        title=doc_record.title,
        filename=doc_record.filename,
        doc_type=doc_record.doc_type,
        supplier_id=doc_record.supplier_id,
        supplier_name=supplier_name,
        chunk_count=doc_record.chunk_count,
        file_size_bytes=doc_record.file_size_bytes,
        created_at=doc_record.created_at,
        summary=doc_record.summary
    )
