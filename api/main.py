from fastapi import FastAPI, Depends
import uvicorn
from pathlib import Path
import sys

# Ajouter le répertoire parent au PYTHONPATH pour résoudre les imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from api.routes import router
from api.security import get_current_username 
# Configuration de l'application FastAPI
app = FastAPI(
    title="API Pipeline Users",
    description="API pour la gestion des utilisateurs avec recherche",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inclure les routes depuis routes.py
app.include_router(router)

def create_app() -> FastAPI:
    """
    Factory function pour créer l'application FastAPI.
    
    Returns:
        FastAPI: Instance configurée de l'application
    """
    return app

@app.get("/users/me/", tags=["secure"],
                  summary="Récupérer l'utilisateur actuel",
        description="Envoi un message a l'utilisateur actuel")
def read_current_user(username: str = Depends(get_current_username)):
    return {"message": f"Bienvenue, {username}"}