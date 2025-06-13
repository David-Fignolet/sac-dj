from enum import Enum

class UserRole(str, Enum):
    AGENT = "agent"
    EXPERT = "expert"
    ADMIN = "admin"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    ERROR = "error"

class ClassificationResult(str, Enum):
    RECEVABLE = "RECEVABLE"
    IRRECEVABLE = "IRRECEVABLE"