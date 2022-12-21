from fastapi import FastAPI

from config.database import create_tables
from routers import auth, todo
from company import companyapi

app = FastAPI()

create_tables()

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(
    companyapi.router,
    tags=['company'],
    prefix="/companyapis",
    responses={410: {"desc": "Internal Error"}},
)
