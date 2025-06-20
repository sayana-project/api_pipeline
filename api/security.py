from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from dotenv import load_dotenv
from pathlib import Path
import secrets
import os

security = HTTPBasic()

# Charger .env à la racine
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    correct_username = os.environ["ADMIN_USERNAME"].encode()
    correct_password = os.environ["ADMIN_PASSWORD"].encode()

    is_valid_username = secrets.compare_digest(credentials.username.encode(), correct_username)
    is_valid_password = secrets.compare_digest(credentials.password.encode(), correct_password)
    
    if not (is_valid_username and is_valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username