from pydantic import BaseModel, Field
from typing import Optional


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str
