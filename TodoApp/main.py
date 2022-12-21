from fastapi import FastAPI

from config.database import create_tables
from routers import auth, todo

app = FastAPI()

create_tables()

app.include_router(auth.router)
app.include_router(todo.router)


