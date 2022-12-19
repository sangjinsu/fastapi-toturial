from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


def get_password_hash(password: str):
    return bcrypt_context.hash(password)


@app.post("/create/user")
async def create_new_user(create_user: CreateUser):
    create_user_model = models.User(email=create_user.email,
                                    first_name=create_user.first_name,
                                    last_name=create_user.last_name,
                                    username=create_user.username,
                                    hashed_password=get_password_hash(create_user.password),
                                    is_active=True
                                    )

    return create_user_model
