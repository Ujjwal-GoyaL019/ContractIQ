from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimeStampMixin


class SupplierDocument(Base, TimeStampMixin):
    __tablename__ = "supplier_documents"
    __table_args__ = (
        Index("ix_doc_supplier_type", "supplier_id", "doc_type"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), default="contract") # contract, sla, delivery_note, risk_notice, compliance
    
    supplier_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=True, index=True)
    qdrant_collection: Mapped[str] = mapped_column(String(100), default="supplier_documents")
    
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="documents")
