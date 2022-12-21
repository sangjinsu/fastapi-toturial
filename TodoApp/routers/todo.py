from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel, Field
from .auth import get_current_user, User, get_user_exception
from models import models
from config.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/todos",
    tags=["todo"],
)


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1 ~ 5")
    complete: bool = Field(default=False)


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()


@router.get("/user")
async def read_all_by_user(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todo).filter(models.Todo.owner_id == user.id).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    new_todo = models.Todo(title=todo.title,
                           description=todo.description,
                           priority=todo.priority,
                           complete=todo.complete,
                           owner_id=user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


@router.get("/{todo_id}")
async def read_todo(todo_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(models.Todo) \
        .filter(models.Todo.id == todo_id) \
        .filter(models.Todo.id == user.id) \
        .first()
    if todo is None:
        raise_http_exception()
    return todo


@router.put("/{todo_id}/", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(todo_id: int, todo: Todo, user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    todo_model = db.query(models.Todo) \
        .filter(models.Todo.id == todo_id) \
        .filter(models.Todo.owner_id == user.id) \
        .first()
    if todo is None:
        raise_http_exception()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    todo_model = db.query(models.Todo) \
        .filter(models.Todo.id == todo_id) \
        .filter(models.Todo.owner_id == user.id) \
        .first()
    if todo_model is None:
        raise_http_exception()
    db.query(models.Todo).filter(models.Todo.id == todo_id).delete()
    db.commit()
    return todo_model


def raise_http_exception():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
