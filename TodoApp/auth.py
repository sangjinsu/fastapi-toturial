from fastapi import FastAPI, HTTPException, Depends
from h11._abnf import status_code
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
