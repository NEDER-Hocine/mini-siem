from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL (file-based for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./siem.db"

# For SQLite in multithreaded environments like FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session
    and makes sure it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

