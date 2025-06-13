from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any
from .enums import UserRole, DocumentStatus, ClassificationResult

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True

class ClassificationRead(BaseModel):
    result: Optional[ClassificationResult] = None
    justification: Optional[str] = None
    confidence_score: Optional[float] = None
    analysis_steps: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentRead(BaseModel):
    id: str
    filename: str
    upload_date: datetime
    status: DocumentStatus
    classification: Optional[ClassificationRead] = None

    class Config:
        from_attributes = True
        
class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str

class HumanValidationCreate(BaseModel):
    validated_result: ClassificationResult
    notes: Optional[str] = None