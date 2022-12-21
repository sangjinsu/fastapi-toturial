from fastapi import FastAPI

from config.database import Base, engine
from routers import auth, todo

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todo.router)


