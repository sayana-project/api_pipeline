from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
import secrets

security = HTTPBasic()

def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    correct_username = b"admin"
    correct_password = b"password"

    is_valid_username = secrets.compare_digest(credentials.username.encode(), correct_username)
    is_valid_password = secrets.compare_digest(credentials.password.encode(), correct_password)

    if not (is_valid_username and is_valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username