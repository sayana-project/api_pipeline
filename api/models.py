from pydantic import BaseModel
from typing import Optional
class User(BaseModel):
    login: str
    id: int
    avatar_url: str
    bio: Optional[str] = None