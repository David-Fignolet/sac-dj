import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin Python
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from sqlalchemy.orm import Session
from app.db.config import SessionLocal, Base
from app.models.document import Document, DocumentStatus, Analysis
from faker import Faker
import random

fake = Faker('fr_FR')

def create_test_data():
    db = SessionLocal()
    try:
        # Créer des documents
        for _ in range(5):
            doc = Document(
                title=fake.sentence(),
                content=fake.text(max_nb_chars=2000),
                summary=fake.paragraph(nb_sentences=3),
                status=random.choice(list(DocumentStatus)),
                document_type=random.choice(["arrêt", "décret", "loi", "circulaire"]),
                reference=f"REF-{fake.unique.random_number(digits=6)}"
            )
            db.add(doc)
            db.flush()  # Pour obtenir l'ID du document
            
            # Ajouter des analyses pour chaque document
            for _ in range(random.randint(1, 3)):
                analysis = Analysis(
                    document_id=doc.id,
                    summary=fake.paragraph(nb_sentences=5),
                    legal_issues="\n- ".join([fake.sentence() for _ in range(3)]),
                    recommendations="\n- ".join([fake.sentence() for _ in range(3)])
                )
                db.add(analysis)
        
        db.commit()
        print("Données de test créées avec succès !")
        
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la création des données de test : {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()