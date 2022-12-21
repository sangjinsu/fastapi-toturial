from fastapi import Depends, APIRouter
from models import models
from config.database import get_db
from sqlalchemy.orm import Session
from schemas.users import UserVerification

from routers.auth import get_current_user, get_user_exception, verify_password, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get("/")
async def get_all_user(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get("/user/{user_id}")
async def user_by_path(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.User).filter(models.User.id == user_id).first()
    if user_model is None:
        return 'Invalid user_id'
    return user_model


@router.get("/user")
async def get_user_by_id_by_query(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.User).filter(models.User.id == user_id).first()
    if user_model is None:
        return 'Invalid user_id'
    return user_model


@router.put("/user/password")
async def change_user_password(user_verification: UserVerification, user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.User).filter(models.Users.id == user.get('id')).first()

    if user_model is not None:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password,
                user_model.hashed_password):
            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return 'successful'
    return 'Invalid user or request'


@router.delete("/user")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    user_model = db.query(models.User).filter(models.User.id == user.get("id")).first()
    if user_model is None:
        return 'Invalid user or request'
    db.query(models.User).filter(models.User.id == user_model.get("id")).delete()
    db.commit()

    return 'Delete Successfully'
