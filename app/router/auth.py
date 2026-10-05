from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas.auth import UserReg, UserLogin
from app.schemas.security import hash_pass, verify_pass, create_access_token

from fastapi.security import OAuth2PasswordBearer
import jwt

from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter( prefix="/auth",tags=["Authentication"])


@router.post("/register")
def register(user_data: UserReg,db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Already Exists")

    new_user = User(name=user_data.name,email=user_data.email,password=hash_pass(user_data.password))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Registered Successfully"}


@router.post("/login")
def login(user_data: UserLogin,db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(status_code=401,detail="Invalid email or password")

    if not verify_pass(user_data.password,user.password):
        raise HTTPException(status_code=401,detail="Invalid email or password")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401,detail="Invalid token")

        user = db.query(User).filter(
            User.id == int(user_id)
        ).first()

        if user is None:
            raise HTTPException(status_code=401,detail="User not found")

        return user

    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail="Invalid or expired token")


@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    }