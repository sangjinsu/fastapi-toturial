from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

import models
from database import SessionLocal, engine
from jose import JWTError, jwt
from datetime import datetime, timedelta

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


class User(BaseModel):
    id: int
    username: int


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_brear = OAuth2PasswordBearer(tokenUrl="token")

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
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    to_encode = dict(sub=username, id=user_id)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update(dict(exp=expire))
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_brear), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise token_exception()
    except JWTError:
        raise token_exception()
    user = db.query(models.User).filter(models.User.username == username, models.User.id == user_id).first()
    if user is None:
        raise get_user_exception()
    return User(username=user.username, id=user.id)


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
        raise token_exception()
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.username, user.id, token_expires)
    return dict(access_token=token, token_type="bearer")


def get_user_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def token_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
