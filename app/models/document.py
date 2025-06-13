from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.config import Base
import enum

class DocumentStatus(str, enum.Enum):
    DRAFT = "brouillon"
    IN_REVIEW = "en_revision"
    PUBLISHED = "publié"
    ARCHIVED = "archivé"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    document_type = Column(String(100), nullable=True)
    reference = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    analyses = relationship("Analysis", back_populates="document")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    summary = Column(Text, nullable=False)
    legal_issues = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    document = relationship("Document", back_populates="analyses")