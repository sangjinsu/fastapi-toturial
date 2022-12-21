from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException, status

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:tkdwlstn@localhost:3306/todoapp"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Connection Error")
    finally:
        db.close()
