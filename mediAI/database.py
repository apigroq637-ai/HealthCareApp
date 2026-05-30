import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Railway injects DATABASE_URL automatically for PostgreSQL.
# Falls back to SQLite for local development.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///medical.db")

# SQLAlchemy requires postgresql:// but Railway provides postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    import models  # noqa: F401 — registers models with Base
    Base.metadata.create_all(bind=engine)
