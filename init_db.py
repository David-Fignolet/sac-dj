from app.database import engine, Base
from app.models import database_models

def init_db():
    # Crée toutes les tables
    print("Création des tables de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_db()