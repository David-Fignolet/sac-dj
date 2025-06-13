import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import pydantic_schemas as schemas, database_models as db_m
from app.services import document_service

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # current_user: db_m.User = Depends(get_current_active_user)
):
    # Pour l'instant, on utilise un utilisateur par défaut
    # En production, utilisez le current_user authentifié
    default_user_id = "00000000-0000-0000-0000-000000000000"
    
    document = await document_service.receive_document(db, file, default_user_id)
    background_tasks.add_task(document_service.process_document_analysis, str(document.id))
    
    return {"message": "Document reçu et en cours d'analyse.", "document_id": document.id}

@router.get("/{document_id}", response_model=schemas.DocumentRead)
async def get_document_details(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(db_m.Document).filter(db_m.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc