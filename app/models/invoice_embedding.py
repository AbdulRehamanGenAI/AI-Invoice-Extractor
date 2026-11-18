from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.session import Base


class InvoiceEmbedding(Base):
    __tablename__ = "invoice_embeddings"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False
    )

    chunk_index = Column(
        Integer,
        nullable=False,
        server_default="0"
    )

    page_number = Column(
    Integer,
    nullable=True
    )

    chunk_text = Column(Text, nullable=False)

    embedding = Column(Vector(768), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )