import jwt
from pwdlib import PasswordHash

from datetime import datetime,timedelta,timezone

from app.core.config import settings

from pydantic import BaseModel, EmailStr

Pass_hash=PasswordHash.recommended()

def hash_pass(password:str):
    return Pass_hash.hash(password)

def verify_pass(password: str, hashed_password: str):
    return Pass_hash.verify(password, hashed_password)


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": str(user_id),"exp": expire}

    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool