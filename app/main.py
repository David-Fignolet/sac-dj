from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import documents

app = FastAPI(
    title="SAC-DJ: Système d'Analyse Cognitive",
    description="API pour l'agent d'analyse de dossiers juridiques.",
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

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenue sur l'API du SAC-DJ"}