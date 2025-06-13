import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from .enums import UserRole, DocumentStatus, ClassificationResult

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.AGENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    content_hash = Column(String, unique=True, index=True, nullable=False)
    file_size = Column(Integer)
    content_type = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by_id = Column(String(36), ForeignKey("users.id"))
    
    classification = relationship("Classification", back_populates="document", uselist=False, cascade="all, delete-orphan")

class Classification(Base):
    __tablename__ = "classifications"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True)
    result = Column(SQLAlchemyEnum(ClassificationResult))
    justification = Column(Text)
    confidence_score = Column(Numeric(5, 4))
    analysis_steps = Column(JSON)
    processing_time_ms = Column(Integer)
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="classification")
    human_validation = relationship("HumanValidation", back_populates="classification", uselist=False, cascade="all, delete-orphan")

class HumanValidation(Base):
    __tablename__ = "human_validations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    classification_id = Column(String(36), ForeignKey("classifications.id"), nullable=False, unique=True)
    validator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    validated_result = Column(SQLAlchemyEnum(ClassificationResult), nullable=False)
    is_ia_correct = Column(Boolean, nullable=False)
    notes = Column(Text)
    validation_date = Column(DateTime(timezone=True), server_default=func.now())

    classification = relationship("Classification", back_populates="human_validation")