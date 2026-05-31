import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# Read from env. For Docker, it'll connect to postgres e.g., postgresql://postgres:postgres@db:5432/fundamental_db
# For local run, fallback to sqlite in the current directory
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite relative path in workspace
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared.db")
    DATABASE_URL = f"sqlite:///{db_path}"

# Connect args needed for SQLite to avoid thread conflicts
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
scoped_db_session = scoped_session(SessionLocal)

Base = declarative_base()

def init_db():
    import shared.models  # Import to register models
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
