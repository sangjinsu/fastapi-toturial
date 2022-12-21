from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException, status

MYSQL_URL = "mysql+pymysql://root:tkdwlstn@localhost:3306/todoapp"
SQLITE_URL = "sqlite:///./todo.db"
SQLALCHEMY_DATABASE_URL = SQLITE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Connection Error")
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
