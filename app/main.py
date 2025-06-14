from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, validation
from app.database import engine
from app.models import database_models

# Créer les tables dans la base de données
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SAC-DJ API",
    description="API pour le système d'analyse et de classification de documents juridiques",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routeurs
app.include_router(documents.router)
app.include_router(validation.router)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API SAC-DJ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
