from pathlib import Path
import shutil

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


def ensure_database_file():
    target = Path(settings.DATABASE_PATH)
    if target.exists():
        return

    if target.parent != Path("."):
        target.parent.mkdir(parents=True, exist_ok=True)

    bundled_db = Path(__file__).resolve().parents[1] / "calorie_tracker.db"
    if bundled_db.exists() and bundled_db.resolve() != target.resolve():
        shutil.copy2(bundled_db, target)


ensure_database_file()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
