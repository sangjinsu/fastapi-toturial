import copy
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Response
from starlette import status
from pydantic import BaseModel, Field

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1 ~ 5")
    complete: bool = Field(default=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    new_todo = models.Todos(title=todo.title,
                            description=todo.description,
                            priority=todo.priority,
                            complete=todo.complete)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


@app.get("/{todo_id}")
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        http_exception()
    return todo


@app.put("/{todo_id}/", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        http_exception()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model


def http_exception():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
