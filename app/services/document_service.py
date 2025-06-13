import uuid
import hashlib
import os
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import database_models as db_m

# Dossier pour les uploads
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

async def receive_document(db: Session, file: UploadFile, user_id: str) -> db_m.Document:
    contents = await file.read()
    content_hash = hashlib.sha256(contents).hexdigest()
    
    # Vérifier si le document existe déjà
    existing_doc = db.query(db_m.Document).filter(db_m.Document.content_hash == content_hash).first()
    if existing_doc:
        return existing_doc

    # Sauvegarder le fichier
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{content_hash}{file_extension}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # Créer le document en base
    new_doc = db_m.Document(
        filename=file.filename,
        content_hash=content_hash,
        file_size=len(contents),
        content_type=file.content_type,
        file_path=file_path,
        uploaded_by_id=user_id,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

async def process_document_analysis(document_id: str):
    from app.database import SessionLocal
    from app.core.agent.graph import compiled_graph
    
    db = SessionLocal()
    try:
        doc = db.query(db_m.Document).filter(db_m.Document.id == document_id).first()
        if not doc:
            return

        doc.status = db_m.DocumentStatus.PROCESSING
        db.commit()

        # Lire le contenu du document
        with open(doc.file_path, "rb") as f:
            text_content = f.read().decode("utf-8", errors="ignore")

        # Exécuter l'analyse
        initial_state = {
            "document_id": str(doc.id),
            "document_content": text_content
        }
        
        final_state = compiled_graph.invoke(initial_state)

        # Sauvegarder les résultats
        classification_result = db_m.Classification(
            document_id=doc.id,
            result=final_state.get("final_classification"),
            justification=final_state.get("final_justification"),
            confidence_score=float(final_state.get("final_confidence", 0)),
            analysis_steps=final_state,
        )
        db.add(classification_result)
        
        doc.status = db_m.DocumentStatus.NEEDS_REVIEW if final_state.get("is_review_required", True) else db_m.DocumentStatus.COMPLETED
        db.commit()

    except Exception as e:
        doc.status = db_m.DocumentStatus.ERROR
        db.commit()
        print(f"Error processing document {document_id}: {e}")
    finally:
        db.close()