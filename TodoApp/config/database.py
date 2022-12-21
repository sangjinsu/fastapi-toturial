from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException, status
from datetime import date, datetime, timedelta

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


def render_query(statement, db_session):
    """
    Generate an SQL expression string with bound parameters rendered inline
    for the given SQLAlchemy statement.
    WARNING: This method of escaping is insecure, incomplete, and for debugging
    purposes only. Executing SQL statements with inline-rendered user values is
    extremely insecure.
    Based on http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query
    """
    if isinstance(statement, Query):
        statement = statement.statement
    dialect = db_session.bind.dialect

    class LiteralCompiler(dialect.statement_compiler):
        def visit_bind_param(
                self, bind_param, within_columns_clause=False, literal_binds=False, **kwargs
        ):
            return self.render_literal_value(bind_param.value, bind_param.type)

        def render_array_value(self, val, item_type):
            if isinstance(val, list):
                return "{}".format(
                    ",".join([self.render_array_value(x, item_type) for x in val])
                )
            return self.render_literal_value(val, item_type)

        def render_literal_value(self, value, type_):
            if isinstance(value, int):
                return str(value)
            elif isinstance(value, (str, date, datetime, timedelta)):
                return "'{}'".format(str(value).replace("'", "''"))
            elif isinstance(value, list):
                return "'{{{}}}'".format(
                    ",".join(
                        [self.render_array_value(x, type_.item_type) for x in value]
                    )
                )
            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return LiteralCompiler(dialect, statement).process(statement)
