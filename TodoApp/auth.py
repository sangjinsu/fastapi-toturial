from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session
from starlette import status

import models
from passlib.context import CryptContext
from database import SessionLocal, engine


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Connection Error")
    finally:
        db.close()


def get_password_hash(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain: str, hashed_password: str):
    return bcrypt_context.verify(plain, hashed_password)


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return True


@app.post("/create/user", status_code=status.HTTP_201_CREATED)
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.User(email=create_user.email,
                                    first_name=create_user.first_name,
                                    last_name=create_user.last_name,
                                    username=create_user.username,
                                    hashed_password=get_password_hash(create_user.password),
                                    is_active=True
                                    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model


@app.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return "User Verified"

