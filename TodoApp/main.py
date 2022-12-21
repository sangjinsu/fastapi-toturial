from fastapi import FastAPI, Depends

from config.database import create_tables
from routers import auth, todo, users
from company import companyapi, dependencies

app = FastAPI()

create_tables()

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(
    companyapi.router,
    tags=['company'],
    prefix="/companyapis",
    dependencies=[Depends(dependencies.get_token_header)],
    responses={410: {"desc": "Internal Error"}},
)
app.include_router(users.router)
