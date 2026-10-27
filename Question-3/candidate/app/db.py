import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Local-first setup: no PostgreSQL, Redis, or Docker required.
# The candidate should preserve SQLite compatibility while fixing the bugs.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db
