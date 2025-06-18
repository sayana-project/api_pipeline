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
    description="API pour la gestion des utilisateurs avec recherche avancée",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inclure les routes depuis routes.py
app.include_router(router, prefix="/api")

# Inclure le http auth depuis security.py


def create_app() -> FastAPI:
    """
    Factory function pour créer l'application FastAPI.
    
    Returns:
        FastAPI: Instance configurée de l'application
    """
    return app


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8022,
        reload=True,
        log_level="info",
        access_log=True
    )
    
@app.get("/api/v1/users/me", tags=["secure"])
def read_current_user(username: str = Depends(get_current_username)):
    return {"message": f"Bienvenue, {username}"}